import base64
from typing import Dict, List


def binary_to_json(binary_data: bytes) -> Dict[str, str]:
    b64 = base64.b64encode(binary_data).decode("utf-8")
    return {"__type__": "base64", "data": b64}


def json_to_binary(json_data: Dict[str, str]) -> bytes:
    return base64.b64decode(json_data["data"].encode("utf-8"))


def recursive_convert_b64dict_to_binary(data: str | Dict | List) -> str | bytes | Dict | List:
    if isinstance(data, dict):
        if data.get("__type__") == "base64":
            return json_to_binary(data)
        else:
            return {k: recursive_convert_b64dict_to_binary(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [recursive_convert_b64dict_to_binary(item) for item in data]
    else:
        return data