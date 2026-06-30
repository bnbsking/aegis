import json
from typing import Dict, List, Optional, Type

import httpx
import requests

from .base import LLMAPI, parse_api_key


class AzureOpenAIChatAPI(LLMAPI):
    def __init__(self, api_key: str, model_name: str):
        self.api_key = parse_api_key(api_key, "azure_openai")
        self.azure_endpoint = f"https://project-emc-llm-foundry.openai.azure.com/openai/deployments/{model_name}/chat/completions?api-version=2024-10-21"
    
    def run(self, prompt: str | List, response_format: Optional[Type] = None) -> str | Dict:
        if isinstance(prompt, str):
            messages = [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ]
        else:
            messages = prompt
        data = {"messages": messages, "max_tokens": None}
        if response_format:
            data["response_format"] = {
                "type": "json_schema",
                "json_schema": {
                    "name": response_format.__name__,
                    "schema": response_format.model_json_schema()
                }
            }
        headers = {"api-key": self.api_key, "Content-Type": "application/json"}
        response = requests.post(self.azure_endpoint, headers=headers, json=data)
        content = response.json()["choices"][0]['message']['content']
        if response_format:
            return json.loads(content)
        return content

    async def arun(self, prompt: str | List, response_format: Optional[Type] = None) -> str | Dict:
        if isinstance(prompt, str):
            messages = [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ]
        else:
            messages = prompt
        data = {"messages": messages, "max_tokens": None}
        if response_format:
            data["response_format"] = {
                "type": "json_schema",
                "json_schema": {
                    "name": response_format.__name__,
                    "schema": response_format.model_json_schema()
                }
            }
        headers = {"api-key": self.api_key, "Content-Type": "application/json"}
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                self.azure_endpoint,
                headers=headers,
                json=data
            )
        content = response.json()["choices"][0]["message"]["content"]
        if response_format:
            return json.loads(content)
        return content


class AzureOpenAIEmbeddingAPI(LLMAPI):
    def __init__(self, api_key: str, model_name: str):
        self.api_key = parse_api_key(api_key, "azure_openai")
        self.azure_endpoint = f"https://project-emc-llm-foundry.openai.azure.com/openai/deployments/{model_name}/embeddings?api-version=2024-10-21"
    
    def run_batch(self, texts: List[str]) -> List[List[float]]:  # process len(texts)
        headers = {"api-key": self.api_key, "Content-Type": "application/json"}
        data = {"input": texts}
        response = requests.post(self.azure_endpoint, headers=headers, json=data)
        data = response.json()['data']
        return [item['embedding'] for item in data]
    