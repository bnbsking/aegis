# Introduction

A pytorch-based OCR API receive pdf_list or img_list

returns list of text.


# Usage

+ download EasyOCR-master.zip from https://github.com/JaidedAI/EasyOCR to this folder

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
