docker run -it -v ../../../_huggingface:/root/.cache/huggingface --rm python:3.12-slim bash -c "
pip install huggingface_hub
hf download google/gemma-4-E4B-it
"
