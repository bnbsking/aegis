# Introduction

Database client SDK

+ Connector

    | database | type       |
    | -        | -          |
    | postgres | relational |         
    | oracle   | relational |
    | qdrant   | vector     |


# SDK Usage

```bash
pip install -e .
```

+ examples: `db_client/tests/integration/db_client/llm_calls/*/*.py`


# Develop (or debug) mode
```bash
docker compose build
docker compose up -d
```
