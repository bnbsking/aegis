import numpy as np
import yaml

from llm_client.llm_calls import init_model


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
    
    def test_run_pydantic(self):
        out = self.llm.run(
            "Generate a fake person information",
            {
                "name": {"type": "string"},
                "age": {"type": "integer"},
                "hobbies": {"type": "array", "items": {"type": "string"}}
            }
        )
        print(out)
        # {'name': 'John Doe', 'age': 30, 'hobbies': ['reading', 'hiking', 'coding']}


class TestGoogleEmbeddingAPI:
    def __init__(self):
        self.llm = init_model(llm_emb_cfg["google"])

    def test_run_batch(self):
        out = self.llm.run_batch(["How are you", "I am fine"])
        out = np.array(out)
        print(out.shape)  # (2, 3072)


if __name__ == "__main__":
    test = TestGoogleChatAPI()
    test.test_run()
    test.test_run_pydantic()

    test = TestGoogleEmbeddingAPI()
    test.test_run_batch()
