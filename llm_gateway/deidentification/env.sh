#!/bin/bash

poetry run pip install -e . --no-deps
## building docker step has already installed all 3rd-party packages (exclude self package: deid)
## init step install the self package: deid only (without internet, with editable mode)

# poetry run pip install -e .[full]

poetry run uvicorn serve:app --reload --host 0.0.0.0 --port 8006

tail -f /dev/null
