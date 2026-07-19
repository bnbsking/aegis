import ast
import base64
import json
import os
import re
from typing import Dict, List

import yaml


class LLMAPI:
    def __init__(self, **kwargs):
        raise NotImplementedError

    def run(self, **kwargs) -> str | Dict:
        raise NotImplementedError
    
    def arun(self, **kwargs) -> str | Dict:
        raise NotImplementedError
    
    def run_batch(self, **kwargs) -> List[List[float]]:
        raise NotImplementedError
    
    def arun_batch(self, **kwargs) -> List[List[float]]:
        raise NotImplementedError


def llm_postprocess(out: str, to_dict: bool = False) -> str | Dict:
    """Mainly for local LLM"""
    out = re.sub(r"<think>[\s\S]*?</think>", "", out)  # qwen style output
    if to_dict:
        try:
            out_ = out.replace("None", "null")
            return json.loads(out_)
        except:
            pass
        try:
            out_ = out.replace("null", "None").replace("false", "False").replace("true", "True")
            return ast.literal_eval(out_)
        except:
            print(f"Failed to parse LLM output: {out}")
            return out
    else:
        return out


def parse_api_key(api_key: str, dict_key: str):
    """Mainly for cloud LLM"""
    if os.path.isfile(api_key):
        with open(api_key, "r") as f:
            return yaml.safe_load(f)[dict_key]
    else:
        return api_key


def img_path_to_openai_url(img_path: str) -> str:
    with open(img_path, "rb") as image_file:
        b64 = base64.b64encode(image_file.read()).decode('utf-8')
    return f"data:image/jpeg;base64,{b64}"
