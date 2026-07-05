# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repo overview

This repo has the following top-level components:

- **`llm_client/`** — a Python SDK for calling LLM APIs (chat + embedding). Includes a `multichat` module for stateful multi-turn chat session management.
- **`llm_server/`** — two independently deployable local model servers:
  - `vllm/` — serves local chat/embedding models via vLLM (OpenAI-compatible, port 8106)
  - `ollama/` — serves local models via Ollama (port 11434)
- **`deidentification/`** — FastAPI service (port 8006) that strips PII with a local LLM before forwarding to a cloud LLM
- **`multichat_demo/`** — FastAPI + static frontend for manually testing `llm_client`'s `multichat` module (port 8007). Test-only scaffold, not a production service.

Each of these is a separate deployable unit with its own `pyproject.toml`/Dockerfile/docker-compose, and depends on `llm_client` (if at all) via an editable path install done at Docker build time (`poetry add -e /sdk/llm_client`) — `llm_client`'s own `pyproject.toml` never gains a web-framework dependency this way. All development, installation, and testing happens inside containers.

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

### deidentification

```bash
# Build context is the repo root (Dockerfile copies both deidentification and llm_client)
cd deidentification
docker compose build
docker compose up -d

# Run integration tests
docker exec -it deid bash -c "poetry run python tests/integration/deid/test_main.py -e /app/exps/main/example"
docker exec -it deid bash -c "poetry run python tests/integration/test_serve.py"
```

### multichat_demo

```bash
# Build context is the repo root (Dockerfile copies both multichat_demo and llm_client)
cd multichat_demo
docker compose build
docker compose up -d
# open http://localhost:8007

# Needs cfgs/api_keys.yaml (gitignored) if cfgs/cfg.yaml points llm_chat_cfg at a cloud backend
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

`multichat/` — stateful multi-turn chat session management, designed to be called from stateless request handlers (e.g. FastAPI):
- `ChatManager` (`manager.py`) — top-level entry point keyed by `account_id`/`session_id`; loads/saves session state around every call, so it holds no in-memory state itself. Methods: `create_session`, `chat`, `edit_and_regenerate`, `edit_title`, `delete_session`, `list_session_id_title`, `get_full_history`.
- `ChatSession` (`session.py`) — one chat turn's logic: appends to history, summarizes old turns via `RecursiveSummarizer` once `limit_len` (token budget) is exceeded, auto-generates a title on the first turn.
- `ChatSessionState` / `ChatMemory` (`memory.py`) — the serializable state (`full_history` for display, `memory.history`/`memory.summary` for what's actually sent to the LLM).
- `JsonChatStorage` (`storage.py`) — default storage backend, one JSON file per `account_id/session_id` under `base_dir` (defaults to `/app/.chat_storage`).

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

### multichat_demo server

`app.py` builds one `ChatManager` at startup from `cfgs/cfg.yaml` (`llm_chat_cfg` + `limit_len`) and exposes it over REST (`/api/sessions*`), plus serves a static vanilla HTML/JS/CSS frontend (`static/`) for manual testing — sidebar session list, chat, per-message "edit & regenerate", title rename. No auth, no tests; it exists purely to exercise `llm_client.multichat` end-to-end through a browser.

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
