from typing import List

import numpy as np
from pydantic import create_model
import yaml

from llm_client.llm_calls import init_model


with open("/app/cfgs/cfg.yaml", "r") as f:
    cfg = yaml.safe_load(f)
llm_chat_cfg = cfg["llm_chat_cfg"]
llm_emb_cfg = cfg["llm_emb_cfg"]


class TestOpenAIChatAPI:
    def __init__(self):
        self.llm = init_model(llm_chat_cfg["openai"])

    def test_run(self):
        out = self.llm.run("How are you")
        print(out)
        # I'm just a computer program, so I don't have feelings, but I'm here and ready to assist you! How can I help you today?
    
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
        # name='Alice Johnson' age=28 hobbies=['reading', 'hiking', 'painting', 'cooking']


class TestOpenAIEmbeddingAPI:
    def __init__(self):
        self.llm = init_model(llm_emb_cfg["openai"])

    def test_run_batch(self):
        out = self.llm.run_batch(["How are you", "I am fine"])
        out = np.array(out)
        print(out.shape)  # (2, 1536)


if __name__ == "__main__":
    obj = TestOpenAIChatAPI()
    obj.test_run()
    obj.test_run_pydantic()

    obj = TestOpenAIEmbeddingAPI()
    obj.test_run_batch()
    