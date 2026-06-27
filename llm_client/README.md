# SDK Usage

```bash
pip install -e .  # default (main)
pip install -e .[google]  # (main + google api)
pip install -e .[openai_vllm]  # (main + openai/vllm api)
```

+ notes
    + local serve llm, get host IP:
        ```bash
        ip addr show | grep eth0
        ```
        please reset IP in cfgs/cfg.yaml


# Develop mode
```bash
docker compose build
docker compose up -d
```


# Functions
+ llm api -> OK
+ context length tools -> OK
+ multi-turn chatting
+ long-term memory
