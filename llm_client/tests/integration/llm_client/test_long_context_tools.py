import yaml

from llm_client.llm_calls import init_model
from llm_client.long_context_tools import (
    get_token_count,
    get_approx_token_count,
    BaseSplitter,
    RecursiveSummarizer,
    RAGFilter
)


with open("/app/tests/integration/llm_client/corpus.txt", "r", encoding="utf-8") as f:
    text = f.read()
with open("/app/cfgs/cfg.yaml", "r", encoding="utf-8") as f:
    cfg = yaml.safe_load(f)


def test_get_token_count():
    token_count = get_token_count(text)
    print(token_count)  # 11981


def test_get_approx_token_count():
    token_count = get_approx_token_count(text)
    print(token_count)  # 12675


class TestBaseSplitter:
    def run(self):
        obj = BaseSplitter(limit_len=int(8192 * 0.85))
        text_list = obj.split_text(text)
        print([get_approx_token_count(piece) for piece in text_list])  # [6935, 5739]


class TestRecursiveSummarizer:
    def __init__(self):
        self.llm = init_model(cfg["llm_chat_cfg"]["azure_openai"])
    
    def run(self):
        obj = RecursiveSummarizer(llm=self.llm, limit_len=int(8192 * 0.85))
        sum_text = obj.run(text, tag="test")
        print(get_approx_token_count(sum_text))  # 3951


class TestRAGFilter:
    def __init__(self):
        self.llm = init_model(cfg["llm_emb_cfg"]["azure_openai"])
    
    def run(self):
        obj = RAGFilter(embedder=self.llm, limit_len=int(8192 // 8), top_k=2)
        question = "Poetry如何管理套件至不同group?"
        filtered_content = obj.rag_filter(question, text)
        print(get_approx_token_count(filtered_content))  # 3675
        print(filtered_content)  # 1706


if __name__ == "__main__":
    1
    # test_get_token_count()
    # test_get_approx_token_count()
    
    #TestBaseSplitter().run()
    
    #TestRecursiveSummarizer().run()
    #TestRAGFilter().run()