## Introduction
使用OCR辨識PDF, 並根據"各廠商客製化", 輸出CSV及寫入Oracle DB.


## MS OCR 必要條件
1. amd64 (x86) 架構硬體, 才能讓此專案 docker image 使用
2. 需要外網
    + 可連到 https://portal.azure.com
    + 和 LinkOne 登記 Public IP


## Usage
+ Put .env into `./` and `./_template` if git block the files


1. Import docker image
    ```bash
    docker load -i 廠商交付docker_image與教學/azure-document-intelligence-layout-v4.tar
    docker load -i 廠商交付docker_image與教學/emc-adi-poc.tar
    ```

2. Build docker images
    ```bash
    docker compose -f _template/adi-docker-compose.yml build
    docker compose build
    ```

3. Launch both container service and host watchdog
    ```bash
    docker network inspect my_shared_network >/dev/null 2>&1 || \
        docker network create my_shared_network  # 僅初次需設定
    docker compose up -d && python3 host_watch.py
    ```


## Implementation Detail
+ container server
    + fastapi receive pdf request
    + copy _template/ to _cases/in_case/[timestamp]
    + watch _cases/out_case/[timestamp]
+ host server
    + watch _cases/in_case
    + do ocr by launching container
    + move from _cases/in_case/[timestamp] to _cases/out_case/[timestamp]
+ notes
    + no more SSH
    + can only deal with one pdf anytime since host server process one pdf anytime only
    + support pdf request only
