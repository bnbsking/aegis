# Introduction

Several common functions for calling llm.

1. **uniform request interface**: `llm_client/llm_client/llm_calls/`
    + client includes
        + azure openai
        + google
        + ollama
        + openai
        + vllm
    + include both
        + chat models
        + embedding models
    + support
        + pydantic response
        + async request (azure openai only)

2. **long context dealing**: `llm_client/llm_client/long_context_tools.py`
    + recursive summarization
    + rag filter

3. **price computing**: `llm_client/llm_client/price.py`

4. **multi-turn chatbot**: `llm_client/llm_client/multichat/`
    + short-term memory with storage
    + long context dealing
    + web UI demo is requires independent environment locates at `multichat_demo/`


# SDK Usage

```bash
pip install -e .  # default (main)
pip install -e .[google]  # (main + google api)
```

+ for testing with local serve llm, get host IP by `ip addr show | grep eth0`

    and reset IP in cfgs/cfg.yaml

+ examples:
    + llm call
        + `llm_client/tests/integration/llm_client/llm_calls/*.py`
    + long context:
        + `llm_client/tests/integration/llm_client/test_long_context_tools.py`    
    + price computing
        + `llm_client/tests/integration/llm_client/test_price.py`
    + multi-turn
        + see `../multichat_demo` (different environment)


# Develop (or debug) mode
```bash
docker compose build
docker compose up -d
```
