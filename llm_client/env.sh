#!/bin/bash

poetry run pip install -e . --no-deps
## building docker step has already installed all 3rd-party packages (exclude self package: llm_tools)
## init step install the self package: llm_tools only (without internet, with editable mode)

tail -f /dev/null
