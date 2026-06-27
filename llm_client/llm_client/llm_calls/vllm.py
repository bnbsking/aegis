from typing import List, Dict

from openai import OpenAI

from .base import LLMAPI, llm_postprocess


class VLLMChat(LLMAPI):
    def __init__(self, model_name: str, base_url: str):
        self.model_name = model_name
        self.client = OpenAI(api_key="fake", base_url=base_url)

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

    def run(self, prompt: str, response_format: str = "", temperature: float = 0.7) -> str | Dict:
        """Pydantic response requires <json_str> specified in response_format e.g. '{"score": int}'"""
        if response_format:
            prompt_ = f"{prompt}\n**Response Format**: Only output a valid json format as below:\n{response_format}"
        else:
            prompt_ = prompt
        args = self._prepare_args(prompt_, temperature)
        response = self.client.chat.completions.create(**args)
        out = response.choices[0].message.content
        out = llm_postprocess(out, to_dict=bool(response_format))
        return out


class VLLMEmbedding(LLMAPI):
    def __init__(self, model_name: str, base_url: str):
        self.model_name = model_name
        self.client = OpenAI(api_key="fake", base_url=base_url)
    
    def _postprocess(self, response) -> List[List[float]]:
        return [d.embedding for d in response.data]
    
    def run_batch(self, texts: List[str]) -> List[List[float]]:  # process len(texts)
        response = self.client.embeddings.create(model=self.model_name, input=texts)
        return self._postprocess(response)
