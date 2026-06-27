#!/bin/bash

CUDA_VISIBLE_DEVICES=0 vllm serve /root/.cache/huggingface/hub/models--Qwen--Qwen3-0.6B/snapshots/c1899de289a04d12100db370d81485cdf75e47ca \
    --tensor-parallel-size 1 \
    --gpu-memory-utilization 0.8 \
    --max-model-len 4096 \
    --port 8106 \
    --served-model-name qwen3:0.6b &

wait
