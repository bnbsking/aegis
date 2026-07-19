from typing import List

import numpy as np
from pydantic import create_model
import yaml

from llm_client.async_funcs import async_executor
from llm_client.llm_calls import init_model
from llm_client.llm_calls.base import img_path_to_openai_url


with open("/app/cfgs/cfg.yaml", "r") as f:
    cfg = yaml.safe_load(f)
llm_chat_cfg = cfg["llm_chat_cfg"]
llm_emb_cfg = cfg["llm_emb_cfg"]


class TestAzureOpenAIChatAPI:
    def __init__(self):
        self.llm = init_model(llm_chat_cfg["azure_openai"])

    def test_run(self):
        out = self.llm.run("How are you")
        print(out)
        # I'm doing great, thank you! How can I assist you today?
    
    def test_run_multi_turn(self):
        out = self.llm.run(
            [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "My name is John. How are you?"},
                {"role": "assistant", "content": "I'm doing great, thank you! How can I assist you today?"},
                {"role": "user", "content": "What is my name?"}
            ]
        )
        print(out)
        # Your name is John. How can I help you further?

    def test_run_pydantic(self):
        fields = {
            "name": (str, ...),
            "age": (int, ...),
            "hobbies": (List[str], ...)
        }
        pymodel = create_model("Person", **fields)
        out = self.llm.run(
            "Generate a fake person information",
            pymodel,
        )
        print(out)
        # {"name":"Emily Johnson","age":29,"hobbies":["painting","cycling","cooking"]}
    
    def test_run_img(self):
        text = "What's in this picture?"
        img_path = "/app/tests/integration/llm_client/llm_calls/dog.jpg"

        out = self.llm.run(
            prompt=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": text},
                        {"type": "image_url", "image_url": {"url": img_path_to_openai_url(img_path)}},
                    ]
                }
            ]
        )
        print(out)
        """
        The picture shows a black and white Border Collie dog sitting on a light-colored surface.
        The dog is looking towards the camera with its head slightly tilted and appears to be happy or curious.
        In the background, there is a glass window or door, through which some bicycles are visible.
        """

    def test_arun(self):
        out = async_executor(
            self.llm.arun,
            [
                {"prompt": "What is the next day of Sunday?"},
                {"prompt": "How much is 15 * 12"}
            ]
        )
        print(out)
        # ['The next day after Sunday is Monday.', '15 * 12 = 180']
    
    def test_arun_pydantic(self):
        fields = {
            "name": (str, ...),
            "age": (int, ...),
            "hobbies": (List[str], ...)
        }
        pymodel = create_model("Person", **fields)
        out = async_executor(
            self.llm.arun,
            [
                {"prompt": "Generate a fake person information", "response_format": pymodel},
                {"prompt": "Generate a fake person information", "response_format": pymodel}
            ]
        )
        print(out)
        # ['{"name":"Alice Johnson","age":29,"hobbies":["painting","cycling","reading"]}',
        # '{"name":"Emily Johnson","age":29,"hobbies":["reading","hiking","painting"]}']


class TestAzureOpenAIEmbeddingAPI:
    def __init__(self):
        self.llm = init_model(llm_emb_cfg["azure_openai"])

    def test_run_batch(self):
        out = self.llm.run_batch(["How are you", "I am fine"])
        out = np.array(out)
        print(out.shape)  # (2, 1536)


if __name__ == "__main__":
    obj = TestAzureOpenAIChatAPI()
    # obj.test_run()
    # obj.test_run_multi_turn()
    # obj.test_run_pydantic()
    obj.test_run_img()
    # obj.test_arun()
    # obj.test_arun_pydantic()
    
    # obj = TestAzureOpenAIEmbeddingAPI()
    # obj.test_run_batch()