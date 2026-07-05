FROM python:3.12-slim

ENV PATH="/root/.local/bin:$PATH"
ENV PYTHONPATH=/app

RUN apt update && \
    apt install -y --no-install-recommends \
        curl \
        vim \
        procps \
        poppler-utils \
        tesseract-ocr \
        tesseract-ocr-eng \
        tesseract-ocr-chi-sim \
        tesseract-ocr-chi-tra
        
RUN curl -sSL https://install.python-poetry.org | python3 -

WORKDIR /app
COPY . /app

RUN poetry install --no-root --no-interaction --no-ansi
