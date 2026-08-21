import base64

import requests
import yaml


def img_path_to_openai_url(img_path: str) -> str:
    with open(img_path, "rb") as image_file:
        b64 = base64.b64encode(image_file.read()).decode('utf-8')
    return f"data:image/jpeg;base64,{b64}"


class BaseRequests:
    def test_cloud_api(self):
        api_request = self.api_request.copy()
        api_request["run_args"] = {
            "prompt": "How are you?"
        }

        response = requests.post(
            "http://localhost:8052/cloud_api",
            json=api_request
        )
        print(response.json())
        # I'm doing great, thank you! How can I assist you today?

    def test_cloud_api_multi_turn(self):
        api_request = self.api_request.copy()
        api_request["run_args"] = {
            "prompt": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "My name is John. How are you?"},
                {"role": "assistant", "content": "I'm doing great, thank you! How can I assist you today?"},
                {"role": "user", "content": "What is my name?"}
            ]
        }

        response = requests.post(
            "http://localhost:8052/cloud_api",
            json=api_request
        )
        print(response.json())
        # Your name is John. How can I help you further?

    def test_cloud_api_pydantic(self):
        api_request = self.api_request.copy()
        api_request["run_args"] = {
            "prompt": "Generate a fake person information",
            "response_format": {
                "name": "str",
                "age": "int",
                "hobbies": ["str"]
            }
        }

        response = requests.post(
            "http://localhost:8052/cloud_api",
            json=api_request
        )
        print(response.json())
        # {"name":"Emily Johnson","age":29,"hobbies":["painting","cycling","cooking"]}

    def test_cloud_api_img(self):
        text = "What's in this picture?"
        img_path = "/app/tests/integration/sdk/llm_client/llm_calls/dog.jpg"

        api_request = self.api_request.copy()
        api_request["run_args"] = {
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

        response = requests.post(
            "http://localhost:8052/cloud_api",
            json=api_request
        )
        print(response.json())
        """
        The picture shows a black and white Border Collie dog sitting on a tiled surface.
        The dog is looking towards the camera with its mouth slightly open, appearing happy and alert.
        In the background, there is a glass window with some bicycles visible behind it.
        """

    def test_cloud_api_arun(self):
        api_request_list = [self.api_request.copy() for _ in range(2)]
        api_request_list[0]["run_args"] = {
            "prompt": "How are you?"
        }
        api_request_list[1]["run_args"] = {
            "prompt": "What is 3 * 5?"
        }

        response = requests.post(
            "http://localhost:8052/async_cloud_api",
            json=api_request_list
        )
        print(response.json())
        # ["I'm doing great, thank you! How can I assist you today?", '3 * 5 = 15']


class TestAzureOpenAI(BaseRequests):
    api_request = {
        "mod_name": "azure_openai",
        "cls_name": "AzureOpenAIChatAPI",
        "init_args": {
            "api_key": yaml.safe_load(open("/app/cfgs/api_keys.yaml", "r"))["azure_openai"],
            "model_name": "gpt-4.1-mini"
        },
        "run_args": None
    }


class TestGoogle(BaseRequests):
    api_request = {
        "mod_name": "google",
        "cls_name": "GoogleChatAPI",
        "init_args": {
            "api_key": yaml.safe_load(open("/app/cfgs/api_keys.yaml", "r"))["google_ky"],
            "model_name": "gemini-3.5-flash-lite"
        },
        "run_args": None
    }


class TestAWS(BaseRequests):
    api_request = {
        "mod_name": "aws",
        "cls_name": "AWSChatAPI",
        "init_args": {
            "profile_name": "emc-ai-poc",
            "region_name": "ap-southeast-1",
            "model_name": "global.anthropic.claude-haiku-4-5-20251001-v1:0"
            # "global.anthropic.claude-sonnet-4-6"
            # "global.anthropic.claude-opus-4-5-20251101-v1:0"
        },
        "run_args": None
    }


if __name__ == "__main__":
    obj = TestAzureOpenAI()
    # obj.test_cloud_api()
    # obj.test_cloud_api_multi_turn()
    # obj.test_cloud_api_pydantic()
    # obj.test_cloud_api_img()
    # obj.test_cloud_api_arun()

    obj = TestGoogle()
    # obj.test_cloud_api()
    # obj.test_cloud_api_multi_turn()
    # obj.test_cloud_api_pydantic()
    # obj.test_cloud_api_img()
    # obj.test_cloud_api_arun()

    obj = TestAWS()
    # obj.test_cloud_api()
    # obj.test_cloud_api_multi_turn()
    # obj.test_cloud_api_pydantic()
    # obj.test_cloud_api_img()
    # obj.test_cloud_api_arun()

    print("All tests passed!")
