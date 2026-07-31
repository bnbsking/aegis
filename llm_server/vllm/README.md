# Introduction

1. confirm
    + llm model is in true folder `../../../_huggingface`
    + docker image is in local registry by `docker images`
    + available GPU by `nvidia-smi`
    + available container name and port by `docker ps -a`
    
2. edit `docker-compose-chat.yaml` or `docker-compose-emb.yaml`

3. edit `serve_chat_llm_.sh` or `serve_emb_llm.sh`

4. launch
    ```bash
    docker compose -f docker-compose-chat.yaml up -d
    ```
    or
    ```bash
    docker compose -f docker-compose-emb.yaml up -d
    ```

+ (Optional) Debugging
    + check server status `docker logs -f <container_name>`
    + send request by llm_client
