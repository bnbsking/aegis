#!/bin/bash

CUDA_VISIBLE_DEVICES=0 vllm serve /root/.cache/huggingface/hub/models--Qwen--Qwen3-Embedding-0.6B/snapshots/97b0c614be4d77ee51c0cef4e5f07c00f9eb65b3/ \
    --tensor-parallel-size 1 \
    --gpu-memory-utilization 0.8 \
    --max-model-len 4096 \
    --port 8106 \
    --served-model-name qwen3-embedding:0.6b &

wait
