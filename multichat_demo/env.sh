#!/bin/bash
## app.py is a standalone entrypoint (no self package to install, unlike deid/),
## PYTHONPATH=/app + the editable llm_client install (done at build time) are enough.

poetry run uvicorn app:app --reload --host 0.0.0.0 --port 8007

tail -f /dev/null
