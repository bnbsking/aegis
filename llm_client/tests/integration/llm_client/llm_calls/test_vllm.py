import numpy as np
import yaml

from llm_client.llm_calls import init_model


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
    
    def test_run_pydantic(self):
        out = self.llm.run(
            "Generate a fake person information",
            "{'name': str, 'age': int, 'hobbies': List[str]}",
        )
        print(out)
        # {'name': 'Lila', 'age': 25, 'hobbies': ['coding', 'reading books', 'hiking']}


class TestVLLMEmbedding:
    def __init__(self):
        self.llm = init_model(llm_emb_cfg["vllm"])

    def test_run_batch(self):
        out = self.llm.run_batch(["How are you", "I am fine"])
        out = np.array(out)
        print(out.shape)  # (2, 1024)


if __name__ == "__main__":
    test = TestVLLMChat()
    test.test_run()
    test.test_run_pydantic()

    test = TestVLLMEmbedding()
    test.test_run_batch()