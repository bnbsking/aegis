import json
from typing import Dict, List, Optional, Type

from openai import OpenAI, AsyncOpenAI

from .base import LLMAPI, parse_api_key
from llm_client.input_converter.response_format import PropertiesResponseFormatConverter


class OpenAIChatAPI(LLMAPI):
    response_format_converter = PropertiesResponseFormatConverter()

    def __init__(self, api_key: str, model_name: str):
        self.model_name = model_name
        api_key_ = parse_api_key(api_key, "openai")
        self.client = OpenAI(api_key=api_key_, base_url=None)
        self.aclient = AsyncOpenAI(api_key=api_key_, base_url=None)

    def _prepare_args(self, prompt: str | List, extra_args: None | Dict = None) -> Dict:
        if isinstance(prompt, str):
            messages = [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ]
        else:
            messages = prompt
        return {
            "model": self.model_name,
            "input": messages,
            **(extra_args or {})
        }
    
    def _postprocess(self, response, response_format: Optional[Type]) -> str | Dict:
        if response_format:
            return json.loads(response.output_text)
        else:
            return response.output_text

    def run(
            self,
            prompt: str | List,
            response_format: None | Dict = None,
            **extra_args,
        ) -> str | Dict:  # process 1 query (prompt)
        args = self._prepare_args(prompt, extra_args)
        if response_format:
            schema = self.response_format_converter.convert(response_format)
            schema["required"] = schema.get("required", [k for k in schema["properties"]])
            schema["additionalProperties"] = schema.get("additionalProperties", False)
            args["text"] = {
                "format": {
                    "name": "ResponseFormat",
                    "type": "json_schema",
                    "schema": schema
                }
            }
        response = self.client.responses.create(**args)
        return self._postprocess(response, response_format)
    
    async def arun(
            self,
            prompt: str | List,
            response_format: None | Dict = None,
            **extra_args,
        ) -> str | Dict:  # process 1 query (prompt)
        args = self._prepare_args(prompt, extra_args)
        if response_format:
            schema = self.response_format_converter.convert(response_format)
            schema["required"] = schema.get("required", [k for k in schema["properties"]])
            schema["additionalProperties"] = schema.get("additionalProperties", False)
            args["text"] = {
                "format": {
                    "name": "ResponseFormat",
                    "type": "json_schema",
                    "schema": schema
                }
            }
        response = await self.aclient.responses.create(**args)
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
    