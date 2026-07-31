# config build by docker compose:
# 
# build:
#       context: ../../
#       dockerfile: llm_gateway/jumphost/Dockerfile


FROM python:3.12-slim

ENV PATH=/root/.local/bin:$PATH
ENV PYTHONPATH=/app

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        curl \
        vim \
        procps \
        unzip \
        less

RUN curl -sSL https://install.python-poetry.org | python3 -

# AWS
RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" \
  -o "/tmp/awscliv2.zip"
RUN rm -rf /tmp/aws
RUN unzip -q /tmp/awscliv2.zip -d /tmp
RUN /tmp/aws/install

WORKDIR /app
COPY llm_gateway/jumphost /app
COPY llm_client /sdk/llm_client

RUN poetry install --no-root --no-interaction --no-ansi
RUN poetry add -e /sdk/llm_client
