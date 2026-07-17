FROM python:3.12-slim

ENV PATH=/root/.local/bin:$PATH
ENV PYTHONPATH=/app

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        curl \
        git \
        vim \
        procps \
        unzip \
        p7zip-full \
        poppler-utils \
        libreoffice

RUN curl -sSL https://install.python-poetry.org | python3 -

WORKDIR /app
COPY . /app

# Install ONLY dependencies
RUN poetry install --no-root --no-interaction --no-ansi
# ❗ DO NOT copy project code here
