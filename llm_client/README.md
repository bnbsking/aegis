# Introduction

This is an llm_client SDK that includes
+ llm api
+ context length tools
+ multi-turn chatting
+ long-term memory


# SDK Usage

```bash
pip install -e .  # default (main)
pip install -e .[google]  # (main + google api)
```

+ for testing with local serve llm, get host IP by `ip addr show | grep eth0` <br>
    and reset IP in cfgs/cfg.yaml
+ **llm api example**: `llm_client/tests/integration/llm_client/llm_calls/*.py`
+ **long context example** `llm_client/tests/integration/llm_client/test_long_context_tools.py`

# Develop mode
```bash
docker compose build
docker compose up -d
```
