# prerequisites: download EasyOCR-master.zip from https://github.com/JaidedAI/EasyOCR

FROM pytorch/pytorch:2.12.1-cuda13.0-cudnn9-runtime

ENV PATH="/root/.local/bin:$PATH"
ENV PYTHONPATH=/app:/usr/local/lib/python3.12/dist-packages

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

COPY EasyOCR-master /app/EasyOCR-master
COPY easyocr_requirements.txt /app/EasyOCR-master/requirements.txt
RUN cd /app/EasyOCR-master &&\
    poetry run pip install -e . &&\
    cd /app

RUN poetry install --no-root --no-interaction --no-ansi
