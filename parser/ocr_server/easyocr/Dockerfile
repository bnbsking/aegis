FROM python:3.12-slim

ENV PATH="/root/.local/bin:$PATH"
ENV PYTHONPATH=/app
ENV PIP_DEFAULT_TIMEOUT=86400

RUN apt update && \
    apt install -y --no-install-recommends \
        curl \
        vim \
        procps \
        poppler-utils \
        libgl1 \
        libglib2.0-0
        
RUN curl -sSL https://install.python-poetry.org | python3 -

WORKDIR /app
COPY . /app

RUN poetry install --no-root --no-interaction --no-ansi
RUN pip uninstall -y torch torchvision torchaudio
RUN pip install --pre torch torchvision torchaudio --index-url https://download.pytorch.org/whl/nightly/cu131
