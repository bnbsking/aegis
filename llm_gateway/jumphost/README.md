# Introduction

A service (gateway) deployed on a computer accessible to cloud API.

**[NOTE] This repo depends on llm_client SDK**


| chat model   | pydantic response | list input for multiturn chat | image input | async |
| -            | -                 | -                             | -           | -     |
| azure_openai | V                 | V                             | V           | V     |
| google       | V                 | V                             | V           | V     |
| openai       | V                 | V                             | V           | V     |
| aws          | V                 | V                             | V           | V     |


# Setup
+ build and launch

```bash
docker compose build
docker compose up -d
```
