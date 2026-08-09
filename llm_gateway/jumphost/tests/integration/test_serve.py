import base64
import os
from typing import Dict

import requests


def img_path_to_openai_url(img_path: str) -> str:
    with open(img_path, "rb") as image_file:
        b64 = base64.b64encode(image_file.read()).decode('utf-8')
    return f"data:image/jpeg;base64,{b64}"


def file_path_to_json(file_path: str) -> Dict[str, str]:
    with open(file_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")
    return {"__type__": "base64", "data": b64}


class TestAzureOpenAI:
    def test_cloud_api(self):
        response = requests.post(
            "http://localhost:8052/cloud_api",
            json={
                "key": "azure_openai",
                "prompt": "How are you?",
            }
        )
        print(response.json())
        # I'm doing great, thank you! How can I assist you today?

    def test_cloud_api_multi_turn(self):
        response = requests.post(
            "http://localhost:8052/cloud_api",
            json={
                "key": "azure_openai",
                "prompt": [
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": "My name is John. How are you?"},
                    {"role": "assistant", "content": "I'm doing great, thank you! How can I assist you today?"},
                    {"role": "user", "content": "What is my name?"}
                ]
            }
        )
        print(response.json())
        # Your name is John. How can I help you further?

    def test_cloud_api_pydantic(self):
        response_format = {
            "name": "str",
            "age": "int",
            "hobbies": ["str"]
        }
        response = requests.post(
            "http://localhost:8052/cloud_api",
            json={
                "key": "azure_openai",
                "prompt": "Generate a fake person information",
                "response_format": response_format
            }
        )
        print(response.json())
        # {"name":"Emily Johnson","age":29,"hobbies":["painting","cycling","cooking"]}

    def test_cloud_api_img(self):
        text = "What's in this picture?"
        img_path = "/app/tests/integration/sdk/llm_client/llm_calls/dog.jpg"

        response = requests.post(
            "http://localhost:8052/cloud_api",
            json={
                "key": "azure_openai",
                "prompt": [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": text},
                            {"type": "image_url", "image_url": {"url": img_path_to_openai_url(img_path)}},
                        ]
                    }
                ]
            }
        )
        print(response.json())
        """
        The picture shows a black and white Border Collie dog sitting on a tiled surface.
        The dog is looking towards the camera with its mouth slightly open, appearing happy and alert.
        In the background, there is a glass window with some bicycles visible behind it.
        """

    def test_cloud_api_arun(self):
        response = requests.post(
            "http://localhost:8052/async_cloud_api",
            json=[
                {
                    "key": "azure_openai",
                    "prompt": "How are you?",
                },
                {
                    "key": "azure_openai",
                    "prompt": "What is 3 * 5?",
                }
            ]
        )
        print(response.json())
        # ["I'm doing great, thank you! How can I assist you today?", '3 * 5 = 15']


class TestGoogle:
    def test_cloud_api(self):
        response = requests.post(
            "http://localhost:8052/cloud_api",
            json={
                "key": "google",
                "prompt": "How are you?",
                "extra_args": {"temperature": 0.0}
            }
        )
        print(response.json())
        # I'm doing great, thank you! How can I assist you today?

    def test_cloud_api_multi_turn(self):
        response = requests.post(
            "http://localhost:8052/cloud_api",
            json={
                "key": "google",
                "prompt": [
                    {"role": "user", "parts": [{"text": "My name is John. How are you?"}]},
                    {"role": "assistant", "parts": [{"text": "I am a large language model, trained by Google."}]},
                    {"role": "user", "parts": [{"text": "What is my name?"}]}
                ]
            }
        )
        print(response.json())
        # Your name is John. How can I help you further?
    
    def test_cloud_api_pydantic(self):
        response_format = {
            "name": {"type": "string"},
            "age": {"type": "integer"},
            "hobbies": {"type": "array", "items": {"type": "string"}}
        }
        response = requests.post(
            "http://localhost:8052/cloud_api",
            json={
                "key": "google",
                "prompt": "Generate a fake person information",
                "response_format": response_format
            }
        )
        print(response.json())
        # {"name":"Emily Johnson","age":29,"hobbies":["painting","cycling","cooking"]}

    def test_cloud_api_img(self):
        text = "What's in this picture?"
        img_path = "/app/tests/integration/sdk/llm_client/llm_calls/dog.jpg"

        b64json = file_path_to_json(img_path)
        response = requests.post(
            "http://localhost:8052/cloud_api",
            json={
                "key": "google",
                "prompt": [
                    {
                        "role": "user",
                        "parts": [
                            {"text": text},
                            {"inline_data": {"mime_type": "image/jpeg", "data": b64json}}
                        ]
                    }
                ]
            }
        )
        print(response.json())
        """
        The picture shows a black and white Border Collie dog sitting on a tiled surface.
        The dog is looking towards the camera with its mouth slightly open, appearing happy and alert.
        In the background, there is a glass window with some bicycles visible behind it.
        """

    def test_cloud_api_arun(self):
        response = requests.post(
            "http://localhost:8052/async_cloud_api",
            json=[
                {
                    "key": "google",
                    "prompt": "How are you?",
                },
                {
                    "key": "google",
                    "prompt": "What is 3 * 5?",
                }
            ]
        )
        print(response.json())
        # ["I'm doing great, thank you! How can I assist you today?", '3 * 5 = 15']


class TestAWS:
    def test_cloud_api(self):
        response = requests.post(
            "http://localhost:8052/cloud_api",
            json={
                "key": "aws",
                "prompt": "How are you?",
            }
        )
        print(response.json())
        # I'm doing great, thank you! How can I assist you today?

    def test_cloud_api_multi_turn(self):
        response = requests.post(
            "http://localhost:8052/cloud_api",
            json={
                "key": "aws",
                "prompt": [
                    {"role": "user", "content": [{"text": "My name is John. How are you?"}]},
                    {"role": "assistant", "content": [{"text": "I'm doing great, thank you! How can I assist you today?"}]},
                    {"role": "user", "content": [{"text": "What is my name?"}]}
                ]
            }
        )
        print(response.json())
        # Your name is John. How can I help you further?

    def test_cloud_api_pydantic(self):
        json_schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer"},
                "hobbies": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["name", "hobbies"]
        }
        response = requests.post(
            "http://localhost:8052/cloud_api",
            json={
                "key": "aws",
                "prompt": "Generate a fake person information",
                "response_format": json_schema
            }
        )
        print(response.json())
        # {"name":"Emily Johnson","age":29,"hobbies":["painting","cycling","cooking"]}

    def test_cloud_api_img(self):
        text = "What's in this picture?"
        img_path = "/app/tests/integration/sdk/llm_client/llm_calls/dog.jpg"

        b64json = file_path_to_json(img_path)
        response = requests.post(
            "http://localhost:8052/cloud_api",
            json={
                "key": "aws",
                "prompt": [
                    {
                        "role": "user",
                        "content": [
                            {"image": {"format": "jpeg", "source": {"bytes": b64json}}},
                            {"text": text},
                        ]
                    }
                ]
            }
        )
        print(response.json())
        """
        The picture shows a black and white Border Collie dog sitting on a tiled surface.
        The dog is looking towards the camera with its mouth slightly open, appearing happy and alert.
        In the background, there is a glass window with some bicycles visible behind it.
        """

    def test_cloud_api_pdf(self):
        text = "請幫我總結這份 PDF 的內容。"
        pdf_path = "/app/tests/integration/sdk/llm_client/llm_calls/dog.pdf"
        
        b64json = file_path_to_json(pdf_path)
        response = requests.post(
            "http://localhost:8052/cloud_api",
            json={
                "key": "aws",
                "prompt": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "document": {
                                    "format": "pdf",
                                    "name": os.path.splitext(os.path.basename(pdf_path))[0],
                                    "source": {
                                        "bytes": b64json,
                                    },
                                }
                            },
                            {
                                "text": text,
                            },
                        ],
                    }
                ]
            }
        )
        print(response.json())
        # 這份 PDF 的內容主要描述了一隻黑白相間的邊境牧羊犬坐在瓷磚表面上。

    def test_cloud_api_arun(self):
        response = requests.post(
            "http://localhost:8052/async_cloud_api",
            json=[
                {
                    "key": "aws",
                    "prompt": "How are you?",
                },
                {
                    "key": "aws",
                    "prompt": "What is 3 * 5?",
                }
            ]
        )
        print(response.json())
        # ["I'm doing great, thank you! How can I assist you today?", '3 * 5 = 15']


if __name__ == "__main__":
    obj = TestAzureOpenAI()
    # obj.test_cloud_api()
    # obj.test_cloud_api_multi_turn()
    # obj.test_cloud_api_pydantic()
    # obj.test_cloud_api_img()
    # obj.test_cloud_api_arun()

    obj = TestGoogle()
    obj.test_cloud_api()
    # obj.test_cloud_api_multi_turn()
    # obj.test_cloud_api_pydantic()
    # obj.test_cloud_api_img()
    # obj.test_cloud_api_arun()

    obj = TestAWS()
    # obj.test_cloud_api()
    # obj.test_cloud_api_multi_turn()
    # obj.test_cloud_api_pydantic()
    # obj.test_cloud_api_img()
    # obj.test_cloud_api_pdf()
    # obj.test_cloud_api_arun()

    print("All tests passed!")
