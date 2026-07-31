# config build by docker compose:
# 
# build:
#       context: ../../
#       dockerfile: llm_gateway/deidentification/Dockerfile


FROM python:3.12-slim

ENV PATH=/root/.local/bin:$PATH
ENV PYTHONPATH=/app

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        curl \
        vim \
        procps

RUN curl -sSL https://install.python-poetry.org | python3 -

WORKDIR /app
COPY llm_gateway/deidentification /app
COPY llm_client /sdk/llm_client

RUN poetry install --no-root --no-interaction --no-ansi
# ❗ DO NOT copy project code here
RUN poetry add -e /sdk/llm_client
