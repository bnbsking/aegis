from typing import Dict, List, Optional, Type

from openai import OpenAI
from pydantic import BaseModel

from .base import LLMAPI, parse_api_key


class OpenAIChatAPI(LLMAPI):
    def __init__(self, api_key: str, model_name: str):
        self.model_name = model_name
        api_key_ = parse_api_key(api_key, "openai")
        self.client = OpenAI(api_key=api_key_, base_url=None)

    def _prepare_args(self, prompt: str | List, temperature: float) -> Dict:
        if isinstance(prompt, str):
            messages = [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ]
        else:
            messages = prompt
        return {
            "model": self.model_name,
            "messages": messages,
            "temperature": temperature
        }
    
    def _postprocess(self, response, response_format: Optional[Type]) -> str | Dict:
        if response_format:
            return response.choices[0].message.parsed
        else:
            return response.choices[0].message.content

    def run(
            self,
            prompt: str | List,
            response_format: Optional[Type[BaseModel]] = None,
            temperature: float = 0.7,
        ) -> str | BaseModel:  # process 1 query (prompt)
        args = self._prepare_args(prompt, temperature)
        if response_format:
            args["response_format"] = response_format
            response = self.client.chat.completions.parse(**args)
        else:
            response = self.client.chat.completions.create(**args)
        return self._postprocess(response, response_format)


class OpenAIEmbeddingAPI(LLMAPI):
    def __init__(self, api_key: str, model_name: str):
        self.model_name = model_name
        api_key_ = parse_api_key(api_key, "openai")
        self.client = OpenAI(api_key=api_key_, base_url=None)
    
    def _postprocess(self, response) -> List[List[float]]:
        return [d.embedding for d in response.data]
    
    def run_batch(self, texts: List[str]) -> List[List[float]]:  # process len(texts)
        response = self.client.embeddings.create(model=self.model_name, input=texts)
        return self._postprocess(response)
    