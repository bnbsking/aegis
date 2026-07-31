# Introduction

1. confirm
    + llm model is in true folder `../../../_ollama`
    + docker image is in local registry by `docker images`
    + available GPU by `nvidia-smi`
    + available container name and port by `docker ps -a`
    
2. edit `docker-compose.yaml`

3. launch
    ```bash
    docker compose up -d
    ```

+ (Optional) Debugging
    + check server status `docker logs -f <container_name>`
    + send request by llm_client
    