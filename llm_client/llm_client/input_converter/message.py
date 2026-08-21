import base64
from typing import Dict, List


class OpenAIMessageToAnyMessage:
    role_map = {
        "system": "assistant",
        "user": "user",
        "assistant": "assistant"
    }

    @staticmethod
    def _is_openai_message(message: List[Dict]) -> bool:
        if not isinstance(message, List):
            return False
        for msg_dict in message:
            if not isinstance(msg_dict, Dict):
                return False
            if "role" not in msg_dict or "content" not in msg_dict:
                return False
            if any("image" in content_dict for content_dict in msg_dict.get("content", [])): 
                return False
        return True

    def to_google(self, message: List[Dict]) -> List[Dict]:
        new_message = []
        for msg_dict in message:
            new_msg_dict = {
                "role": self.role_map.get(msg_dict["role"], msg_dict["role"]),
                "parts": []
            }
            if isinstance(msg_dict["content"], str):
                new_msg_dict["parts"].append({"text": msg_dict["content"]})
            elif isinstance(msg_dict["content"], List):
                for content in msg_dict["content"]:
                    if "text" in content:
                        new_msg_dict["parts"].append({"text": content["text"]})
                    elif "image_url" in content:
                        b64 = content["image_url"]["url"].split(",")[1]
                        binary = base64.b64decode(b64)
                        new_msg_dict["parts"].append(
                            {
                                "inline_data": {
                                    "mime_type": "image/jpeg",
                                    "data": binary
                                }
                            }
                        )
            new_message.append(new_msg_dict)
        return new_message

    def to_aws(self, message: List[Dict]) -> List[Dict]:
        new_message = []
        for msg_dict in message:
            new_msg_dict = {
                "role": self.role_map.get(msg_dict["role"], msg_dict["role"]),
                "content": []
            }
            if isinstance(msg_dict["content"], str):
                new_msg_dict["content"].append({"text": msg_dict["content"]})
            elif isinstance(msg_dict["content"], List):
                for content in msg_dict["content"]:
                    if "text" in content:
                        new_msg_dict["content"].append({"text": content["text"]})
                    elif "image_url" in content:  # only diff from openai
                        b64 = content["image_url"]["url"].split(",")[1]
                        binary = base64.b64decode(b64)
                        new_msg_dict["content"].append(
                            {
                                "image": {
                                    "format": "jpeg",
                                    "source": {"bytes": binary}
                                }
                            }
                        )
            new_message.append(new_msg_dict)
        return new_message

    def convert(self, message: List[Dict], target: str) -> List[Dict]:
        if not self._is_openai_message(message):
            return message
        elif not hasattr(self, f"to_{target}"):
            raise ValueError(f"Unsupported target: {target}")
        func = getattr(self, f"to_{target}", None)
        return func(message)
        