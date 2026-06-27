from typing import Dict, List

from google import genai
from google.genai.types import EmbedContentConfig, GenerateContentConfig

from .base import LLMAPI, parse_api_key


class GoogleChatAPI(LLMAPI):
    def __init__(self, api_key: str, model_name: str):
        self.model_name = model_name
        api_key_ = parse_api_key(api_key, "google")
        self.client = genai.Client(api_key=api_key_)

    def _prepare_args(self, response_format: dict, temperature: float) -> GenerateContentConfig:
        if response_format:
            return GenerateContentConfig(
                    temperature=temperature,
                    response_mime_type="application/json",
                    response_schema={
                        "type": "object",
                        "properties": response_format,
                    }
                )
        else:
            return GenerateContentConfig(temperature=temperature)

    def _postprocess(self, response, response_format: Dict) -> str | Dict:
        return response.parsed if response_format else response.text
    
    def run(
            self,
            prompt: str | List,
            response_format: dict = None,
            temperature: float = 0.7,
        ) -> str | Dict:  # process 1 query (prompt) at once
        cfg = self._prepare_args(response_format, temperature)
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt,
            config=cfg
        )
        return self._postprocess(response, response_format)


class GoogleEmbeddingAPI(LLMAPI):
    def __init__(self, api_key: str, model_name: str):
        self.model_name = model_name
        api_key_ = parse_api_key(api_key, "google")
        self.client = genai.Client(api_key=api_key_)
    
    def _prepare_args(self, dim: int) -> EmbedContentConfig:
        return EmbedContentConfig(task_type="RETRIEVAL_DOCUMENT", output_dimensionality=dim)
    
    def _postprocess(self, result) -> List[List[float]]:
        return [x.values for x in result.embeddings]
    
    def run_batch(self, texts: List[str], dim: int = 3072) -> List[List[float]]:  # process len(texts)
        cfg = self._prepare_args(dim)
        result = self.client.models.embed_content(model=self.model_name, contents=texts, config=cfg)
        return self._postprocess(result)
