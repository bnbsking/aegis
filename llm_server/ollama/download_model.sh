docker run -it -v ../../../_ollama:/root/.ollama --rm python:3.12-slim bash -c "
ollama pull qwen3:0.6b
ollama list
"
