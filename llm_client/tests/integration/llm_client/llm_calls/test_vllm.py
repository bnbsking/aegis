import numpy as np
import yaml

from llm_client.llm_calls import init_model
from llm_client.llm_calls.base import img_path_to_openai_url


with open("/app/cfgs/cfg.yaml", "r") as f:
    cfg = yaml.safe_load(f)
llm_chat_cfg = cfg["llm_chat_cfg"]
llm_emb_cfg = cfg["llm_emb_cfg"]


class TestVLLMChat:
    def __init__(self):
        self.llm = init_model(llm_chat_cfg["vllm"])

    def test_run(self):
        out = self.llm.run("How are you")
        print(out)
        # I'm here to help! How can I assist you today?
    
    def test_run_multi_turn(self):
        out = self.llm.run(
            [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "My name is James, I am an engineer."},
                {"role": "assistant", "content": "Hi James! Engineer here. How can I assist you today?"},
                {"role": "user", "content": "What is my name?"}
            ]
        )
        print(out)
        # Hi there, your name is James! 😊 What can I help you with?

    def test_run_pydantic(self):
        out = self.llm.run(
            "Generate a fake person information",
            "{'name': str, 'age': int, 'hobbies': List[str]}",
        )
        print(out)
        # {'name': 'Lila', 'age': 25, 'hobbies': ['coding', 'reading books', 'hiking']}
    
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
        Based on the picture, here is what is in it:

        *   **A dog:** The central subject is a beautiful, medium-to-large dog. It appears to be a black and white breed, possibly a Border Collie or a similar herding breed, with prominent black fur, white markings on its chest, muzzle, and legs, and a fluffy black and white coat. It is sitting attentively.
        *   **A surface/ground:** The dog is sitting on a clean, white, flat surface, which looks like a patio, balcony, or modern flooring.
        *   **Background elements:** The background is somewhat blurred (shallow depth of field), but you can make out:
            *   **Glass/Windows:** There are large glass windows or doors behind the dog.
            *   **Outdoor/Urban setting:** Through the glass, you can see hints of an outdoor environment, including what looks like parked vehicles or bicycles, suggesting the photo was taken near a building or in an urban/suburban setting.
            *   **Structural elements:** There is a plain, light-colored (possibly gray or white) structure dividing the space behind the dog.
        """


class TestVLLMEmbedding:
    def __init__(self):
        self.llm = init_model(llm_emb_cfg["vllm"])

    def test_run_batch(self):
        out = self.llm.run_batch(["How are you", "I am fine"])
        out = np.array(out)
        print(out.shape)  # (2, 1024)


if __name__ == "__main__":
    obj = TestVLLMChat()
    #obj.test_run()
    #obj.test_run_multi_turn()
    #obj.test_run_pydantic()
    obj.test_run_img()

    #obj = TestVLLMEmbedding()
    #obj.test_run_batch()