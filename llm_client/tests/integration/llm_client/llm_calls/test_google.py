import numpy as np
import yaml

from llm_client.async_funcs import async_executor
from llm_client.llm_calls import init_model
from llm_client.llm_calls.base import img_path_to_openai_url


with open("/app/cfgs/cfg.yaml", "r") as f:
    cfg = yaml.safe_load(f)
llm_chat_cfg = cfg["llm_chat_cfg"]
llm_emb_cfg = cfg["llm_emb_cfg"]


class TestGoogleChatAPI:
    def __init__(self):
        self.llm = init_model(llm_chat_cfg["google"])

    def test_run(self):
        out = self.llm.run("How are you")
        print(out)
        # I am a large language model, trained by Google.
    
    def test_run_multi_turn(self):
        out = self.llm.run(
            [
                {"role": "user", "parts": [{"text": "My name is John. How are you?"}]},
                {"role": "assistant", "parts": [{"text": "I am a large language model, trained by Google."}]},
                {"role": "user", "parts": [{"text": "What is my name?"}]}
            ]
        )
        print(out)
        # Your name is John. How can I help you today?

    def test_run_multi_turn_openai_format(self):
        out = self.llm.run(
            [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "My name is John. How are you?"},
                {"role": "assistant", "content": "I'm doing great, thank you! How can I assist you today?"},
                {"role": "user", "content": "What is my name?"}
            ]
        )
        print(out)

    def test_run_pydantic(self):
        out = self.llm.run(
            "Generate a fake person information",
            {
                "name": "str",
                "age": "int",
                "hobbies": ["str"]
            },
        )
        print(out)
        # {"name":"Emily Johnson","age":29,"hobbies":["painting","cycling","cooking"]}

    def test_run_pydantic_raw(self):
        out = self.llm.run(
            "Generate a fake person information",
            {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "age": {"type": "integer"},
                    "hobbies": {"type": "array", "items": {"type": "string"}}
                }
            }
        )
        print(out)
        # {'name': 'John Doe', 'age': 30, 'hobbies': ['reading', 'hiking', 'coding']}
    
    def test_run_img(self):
        text = "What's in this picture?"
        img_path = "/app/tests/integration/llm_client/llm_calls/dog.jpg"

        out = self.llm.run(
            prompt=[
                {
                    "role": "user",
                    "parts": [
                        {"text": text},
                        {"inline_data": {"mime_type": "image/jpeg", "data": open(img_path, "rb").read()}}
                    ]
                }
            ]
        )
        print(out)
        """
        This picture shows a black and white **Border Collie** dog. 
        The dog is sitting upright on a light-colored tiled surface, looking directly at the camera with an alert,
        friendly expression and its mouth slightly open.
        In the background, there is a modern building with gray panels and large glass windows reflecting bicycles.
        """

    def test_run_img_openai_format(self):
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
                {"prompt": "How are you?"},
                {"prompt": "What day is it today?"}
            ]
        )
        print(out)
        """
        [
        "I'm doing great, thank you for asking! How are you doing today? How can I help you?",
        'Today is Wednesday, May 15, 2024.'
        ]
        """


class TestGoogleEmbeddingAPI:
    def __init__(self):
        self.llm = init_model(llm_emb_cfg["google"])

    def test_run_batch(self):
        out = self.llm.run_batch(["How are you", "I am fine"])
        out = np.array(out)
        print(out.shape)  # (2, 3072)


if __name__ == "__main__":
    obj = TestGoogleChatAPI()
    # obj.test_run()
    # obj.test_run_multi_turn()
    # obj.test_run_multi_turn_openai_format()
    # obj.test_run_pydantic()
    # obj.test_run_pydantic_raw()
    # obj.test_run_img()
    # obj.test_run_img_openai_format()
    # obj.test_arun()

    # obj = TestGoogleEmbeddingAPI()
    # obj.test_run_batch()
