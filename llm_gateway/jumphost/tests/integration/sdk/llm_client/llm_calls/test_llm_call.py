import yaml

from llm_client.async_funcs import async_executor
from llm_client.llm_calls import init_model
from llm_client.llm_calls.base import img_path_to_openai_url


class BaseLLMCall:
    def __init__(self):
        api_key = yaml.safe_load(open("/app/cfgs/api_keys.yaml", "r"))["azure_openai"]
        self.llm = init_model(
            {
                "mod_name": "azure_openai",
                "cls_name": "AzureOpenAIChatAPI",
                "args": {
                    "api_key": api_key,
                    "model_name": "gpt-4.1-mini"
                }
            }
        )

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
                "properties": {
                    "name": {"type": "string"},
                    "age": {"type": "integer"},
                    "hobbies": {"type": "array", "items": {"type": "string"}}
                },
                "type": "object"
            },
        )
        print(out)
        # {"name":"Emily Johnson","age":29,"hobbies":["painting","cycling","cooking"]}

    def test_run_img(self):
        text = "What's in this picture?"
        img_path = "/app/tests/integration/sdk/llm_client/llm_calls/dog.jpg"

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


class TestAzureOpenAI(BaseLLMCall):
    def __init__(self):
        api_key = yaml.safe_load(open("/app/cfgs/api_keys.yaml", "r"))["azure_openai"]
        self.llm = init_model(
            {
                "mod_name": "azure_openai",
                "cls_name": "AzureOpenAIChatAPI",
                "args": {
                    "api_key": api_key,
                    "model_name": "gpt-4.1-mini"
                }
            }
        )


class TestGoogle(BaseLLMCall):
    def __init__(self):
        api_key = yaml.safe_load(open("/app/cfgs/api_keys.yaml", "r"))["google_ky"]
        self.llm = init_model(
            {
                "mod_name": "google",
                "cls_name": "GoogleChatAPI",
                "args": {
                    "api_key": api_key,
                    "model_name": "gemini-3.5-flash"
                }
            }
        )


class TestAWS(BaseLLMCall):
    def __init__(self):
        self.llm = init_model(
            {
                "mod_name": "aws",
                "cls_name": "AWSChatAPI",
                "args": {
                    "profile_name": "emc-ai-poc",
                    "region_name": "ap-southeast-1",
                    "model_name": "global.anthropic.claude-haiku-4-5-20251001-v1:0",
                    # "global.anthropic.claude-haiku-4-5-20251001-v1:0"
                    # "global.anthropic.claude-sonnet-4-6"
                    # "global.anthropic.claude-opus-4-5-20251101-v1:0"
                }
            }
        )

if __name__ == "__main__":
    obj = TestAzureOpenAI()
    # obj.test_run()
    # obj.test_run_multi_turn()
    # obj.test_run_pydantic()
    # obj.test_run_pydantic_raw()
    # obj.test_run_img()
    # obj.test_arun()

    obj = TestGoogle()
    # obj.test_run()
    # obj.test_run_multi_turn()
    # obj.test_run_pydantic()
    # obj.test_run_pydantic_raw()
    # obj.test_run_img()
    # obj.test_arun()

    obj = TestAWS()
    # obj.test_run()
    # obj.test_run_multi_turn()
    # obj.test_run_pydantic()
    # obj.test_run_pydantic_raw()
    obj.test_run_img()
    obj.test_arun()
    