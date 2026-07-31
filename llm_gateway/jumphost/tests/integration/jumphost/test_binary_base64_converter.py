import base64
import json
from typing import Dict

from jumphost.binary_base64_converter import (
    binary_to_json,
    json_to_binary,
    recursive_convert_b64dict_to_binary
)


def test_binary_to_json():
    img_path = "/app/tests/integration/sdk/llm_client/llm_calls/dog.jpg"

    binary = open(img_path, "rb").read()
    b64_json = binary_to_json(binary)

    json.dumps(b64_json)  # Ensure it can be serialized to JSON
    assert isinstance(b64_json, dict)


def test_json_to_binary():
    img_path = "/app/tests/integration/sdk/llm_client/llm_calls/dog.jpg"

    binary = open(img_path, "rb").read()
    b64_json = binary_to_json(binary)
    binary_converted_back = json_to_binary(b64_json)

    assert binary == binary_converted_back


class TestRecursiveConvertB64DictToBinary:
    @staticmethod
    def _file_path_to_json(file_path: str) -> Dict[str, str]:
        with open(file_path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode("utf-8")
        return {"__type__": "base64", "data": b64}

    def _get_user_message(self):
        text = "What's in this picture?"
        img_path = "/app/tests/integration/sdk/llm_client/llm_calls/dog.jpg"

        b64json = self._file_path_to_json(img_path)
        return [
            {
                "role": "user",
                "parts": [
                    {"text": text},
                    {"inline_data": {"mime_type": "image/jpeg", "data": b64json}}
                ]
            }
        ]

    def test_run(self):
        user_message = self._get_user_message()
        converted_message = recursive_convert_b64dict_to_binary(user_message)
        
        assert isinstance(converted_message, list)
        assert isinstance(converted_message[0], dict)
        assert isinstance(converted_message[0]["parts"], list)
        assert isinstance(converted_message[0]["parts"][1]["inline_data"]["data"], bytes)


if __name__ == "__main__":
    test_binary_to_json()
    test_json_to_binary()

    obj = TestRecursiveConvertB64DictToBinary()
    obj.test_run()

    print("All tests passed!")
    