# Introduction

Web ui manually testing for multi-turn chatbot in llm_client.

Note that this is just demo, not production service — no auth, JSON-file storage only.

![ui](pics/ui.png)


# Usage

```bash
docker compose build
docker compose up -d
# open browser http://localhost:8007
```

Chat storage persists under `./.chat_storage` (bind-mounted, gitignored).

Set the LLM config in `cfgs/cfg.yaml`.
