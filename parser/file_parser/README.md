# Introduction

An SDK that parse document to pure string or json 

| input format   | mode         | output format |
| -              | -            | -             |
| pdf, docx, doc | text-only    | str  |
| :              | hybrid       | str  |
| :              | ocr-only     | json |
| csv, xlsx, xls | to_str=True  | str  |
| :              | to_str=False | json |
| text           |              | str  |
| jpg, png       |              | str  |
| msg            |              | json |
| pptx, ppt      |              | json |

+ **[NOTE] If OCR is required, please launch OCR server as the interface in ocr_server/ service**


# SDK Usage

```bash
apt update && apt install \
    unzip \
    p7zip-full \
    poppler-utils \
    libreoffice

pip install -e .
```


#  Develop (or debug) mode

+ note
    + if ocr is required (e.g. pdf/word/image), launch the server in advance
    + additional args of parsers is in `cfgs/cfg.yaml`

+ build and launch environment

```bash
docker compose build
docker compose up -d
```

+ test
```bash
docker exec -it file_parser bash
poetry run python tests/integration/file_parser/test_init.py
```
