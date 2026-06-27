# SDK Usage
```bash
pip install -e .  # default (main)
pip install -e .[google]  # (main + google api)
pip install -e .[openai_vllm]  # (main + openai/vllm api)
```


# Note
+ local serve llm, get host IP:
```bash
ip addr show | grep eth0
```
please reset IP in cfgs/cfg.yaml


# Testing environment setup
1. (If need ollama or vllm) pull docker and rename

2. build docker and run

```bash
docker compose build
docker compose up -d
```


# Functions
+ llm api
+ context length tools
+ multi-turn chatting
+ long-term memory