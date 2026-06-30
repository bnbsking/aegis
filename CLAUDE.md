# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repo overview

This repo has two top-level components:

- **`llm_client/`** — a Python SDK for calling LLM APIs (chat + embedding)
- **`llm_server/`** — three independently deployable servers:
  - `vllm/` — serves local chat/embedding models via vLLM (OpenAI-compatible, port 8106)
  - `ollama/` — serves local models via Ollama (port 11434)
  - `deidentification/` — FastAPI service (port 8006) that strips PII with a local LLM before forwarding to a cloud LLM

Both components run in Docker; all development, installation, and testing happens inside containers.

## Commands

All commands run inside the relevant Docker container (e.g. `docker exec -it llm_client bash`).

### llm_client

```bash
# Build & start
cd llm_client
docker compose build
docker compose up -d

# Install SDK in editable mode (done automatically by env.sh on container start)
poetry run pip install -e . --no-deps

# Run a single integration test
docker exec -it llm_client bash -c "poetry run python tests/integration/llm_client/llm_calls/test_openai.py"
docker exec -it llm_client bash -c "poetry run python tests/integration/llm_client/test_long_context_tools.py"
```

### llm_server / deidentification

```bash
# Build context is the repo root (Dockerfile copies both llm_server/deidentification and llm_client)
cd llm_server/deidentification
docker compose build
docker compose up -d

# Run integration tests
docker exec -it deid bash -c "poetry run python tests/integration/deid/test_main.py -e /app/exps/main/example"
docker exec -it deid bash -c "poetry run python tests/integration/test_serve.py"
```

### Local LLM servers

```bash
# vLLM (chat)
cd llm_server/vllm && docker compose -f docker-compose-chat.yaml up -d

# Ollama
cd llm_server/ollama && docker compose up -d
```

## Architecture

### llm_client SDK

`llm_client/llm_calls/` contains one file per backend, all inheriting from `LLMAPI` (`base.py`):

| Class | File | Backend |
|---|---|---|
| `VLLMChat` / `VLLMEmbedding` | `vllm.py` | Local vLLM server |
| `OllamaChat` / `OllamaEmbedding` | `ollama.py` | Local Ollama server |
| `OpenAIChatAPI` / `OpenAIEmbeddingAPI` | `openai.py` | OpenAI cloud |
| `AzureOpenAIChatAPI` / `AzureOpenAIEmbeddingAPI` | `azure_openai.py` | Azure OpenAI |
| `GoogleChatAPI` / `GoogleEmbeddingAPI` | `google.py` | Google Gemini |

`init_model(cfg_dict)` is the factory — it reads `mod_name`/`cls_name`/`args` from a dict (typically loaded from `cfgs/cfg.yaml`) and dynamically imports the right class.

`LLMAPI` interface: `run()` for a single call, `arun()` for async, `run_batch()` / `arun_batch()` for embeddings.

`long_context_tools.py` provides:
- `BaseSplitter` — splits text into token-bounded chunks
- `RecursiveSummarizer` — reduces long text by LLM summarization
- `RAGFilter` — selects top-k relevant chunks via embedding cosine similarity

`async_funcs.async_executor(afunc, args_list)` — runs many `arun` coroutines in parallel with `asyncio.gather`.

`price.py` — cost estimation using `cfgs/price.csv` (USD per million tokens).

### deidentification server

The deid pipeline runs in two stages before every cloud API call:

1. **Deid** (local LLM) — replaces PII with `[_]` placeholders using a prompt from `deid.txt`
2. **Eval** (local LLM) — verifies no PII remains using `eval.txt`, expects `{"has_pii": bool}` JSON

This is implemented in `deid/deid_collections.py` (`ExampleDeid`) with class-level LRU caches for both stages. Long texts are split by `BaseSplitter` before processing.

`DeidPipeline` (`deid/main.py`) wraps a `BaseDeid` subclass and marks output as `[Deid_failed]` if eval rejects it.

`serve.py` exposes two FastAPI endpoints:
- `POST /cloud_api` — sync single request
- `POST /async_cloud_api` — async batch; deid runs sequentially, cloud LLM calls are parallelised via `async_executor`

Both accept `response_format_dict` (a JSON-serialisable schema) which is converted to a Pydantic model by `deid/response_formatting.py` (`schema_to_model`).

The prompt template uses `{{ deid_text }}` as the placeholder for deidentified content.

### Configuration

- `cfgs/cfg.yaml` — model configurations keyed by provider name; set the `base_url` IP using `ip addr show | grep eth0` for local LLM servers
- `cfgs/api_keys.yaml` — cloud API keys (referenced by path in cfg.yaml; `parse_api_key` loads the file if the value is a file path)
- `cfgs/serve.yaml` — deid server config: which cloud LLM to use and the list of deid pipeline configs

### Adding a new deid use case

1. Create a folder under `exps/main/` with `cfg.yaml`, `prompts/deid.txt`, `prompts/eval.txt`, and `data/*.txt`
2. Run evaluation to validate local LLM+prompts actually remove PII
3. Register the key → cfg path in `cfgs/serve.yaml`

### Adding a new LLM backend

Subclass `LLMAPI` in a new file under `llm_client/llm_calls/`, implement `run`/`arun`/`run_batch`/`arun_batch` as needed, and add an entry to `cfgs/cfg.yaml`.
