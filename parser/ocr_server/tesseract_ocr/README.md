# Introduction

A lightweight OCR API receive pdf_list or img_list

returns list of text.


# usage

+ launch service 
    ```bash
    docker compose build
    docker compose up -d
    ```

+ debug
    ```bash
    docker exec -it tesseract_ocr bash
    poetry run python tests/integration/test_serve.py
    ```
