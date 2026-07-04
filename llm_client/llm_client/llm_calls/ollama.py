import requests
from typing import List, Dict

from .base import LLMAPI, llm_postprocess


class OllamaChat(LLMAPI):
    def __init__(self, model_name: str, base_url: str):
        self.model_name = model_name
        self.base_url = base_url

    def run(self, prompt: str | List, response_format: str = "") -> str | Dict:
        """Pydantic response requires <json_str> specified in response_format e.g. '{"score": int}'"""
        if response_format:
            prompt_ = f"{prompt}\n**Response Format**: Only output a valid json format as below:\n{response_format}"
        else:
            prompt_ = str(prompt)
        payload = {"model": self.model_name, "prompt": prompt_, "stream": False}
        response = requests.post(self.base_url, json=payload)
        out = response.json()["response"]
        out = llm_postprocess(out, to_dict=bool(response_format))
        return out



class OllamaEmbedding(LLMAPI):
    def __init__(self, model_name: str, base_url: str):
        self.base_url = base_url
        self.model_name = model_name
    
    def run_batch(self, texts: List[str]) -> List[List[float]]:
        payload = {"model": self.model_name, "input": [str(t) for t in texts]}
        response = requests.post(self.base_url, json=payload)
        return response.json()["embeddings"]
