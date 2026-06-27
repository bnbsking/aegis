from typing import Dict, List, Optional

import requests

from .base import LLMAPI


class JumpHostChatAPI(LLMAPI):
    def __init__(self, base_url_sync: str, base_url_async: str):
        self.base_url_sync = base_url_sync
        self.base_url_async = base_url_async
    
    def run(
            self,
            prompt: str | List,
            response_format: Optional[Dict] = None
        ) -> str | Dict:
        data = {"prompt": prompt}
        if response_format:
            data["response_format_dict"] = response_format
        response = requests.post(self.base_url_sync, json=data)
        return response.json()

    def arun(
            self,
            prompt_list: List[str | List],
            response_format_list: Optional[List[Dict]] = None
        ) -> str | Dict:
        data_list = []
        for i, prompt in enumerate(prompt_list):
            data = {"prompt": prompt}
            if response_format_list and i < len(response_format_list):
                data["response_format_dict"] = response_format_list[i]
            data_list.append(data)
        response = requests.post(self.base_url_async, json=data_list)
        return response.json()
    