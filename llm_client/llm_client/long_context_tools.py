import logging
import re
from typing import List

try:
    import tiktoken
except ImportError:
    tiktoken = None

from .llm_calls import LLMAPI


logger = logging.getLogger(__name__)


def get_token_count(text: str, model: str = "gpt-4.1") -> int:
    if tiktoken is None:
        raise ImportError("tiktoken is not installed. Run: pip install tiktoken")
    enc = tiktoken.encoding_for_model(model)
    return len(enc.encode(text))


def get_approx_token_count(text: str) -> int:
    """
    Estimate token count for mixed Chinese/English text.
    Heuristic tuned for modern BPE tokenizers (Qwen/LLaMA/GPT style).
    """
    chinese_chars = re.findall(r'[\u4e00-\u9fff]', text)
    english_words = re.findall(r'[A-Za-z]+', text)
    numbers = re.findall(r'\d+', text)
    punctuation = re.findall(r'[^\w\s\u4e00-\u9fff]', text)

    tokens = len(chinese_chars) * 1\
        + int(len(english_words) * 1.3)\
        + len(numbers) * 1\
        + len(punctuation) * 1

    return tokens


class BaseSplitter:
    def __init__(self, limit_len: int = int(8192 * 0.85), step: int = 500):
        self.limit_len = limit_len
        self.step = step

    def split_text(self, text: str) -> List[str]:
        raw_text_list = []
        for i in range(0, len(text), self.step):
            piece = text[i: i + self.step]
            if not raw_text_list or get_approx_token_count(raw_text_list[-1] + piece) > self.limit_len:
                raw_text_list.append(piece)
            else:
                raw_text_list[-1] += piece
        return raw_text_list


class BaseSummarizer:
    def run(self, text: str) -> str:
        raise NotImplementedError


class RecursiveSummarizer(BaseSummarizer):
    def __init__(self, llm: LLMAPI, limit_len: int = int(8192 * 0.85)):
        self.llm = llm
        self.limit_len = limit_len
        self.spliter = BaseSplitter(limit_len=self.limit_len)

    def _recursive_sum(self, text: str) -> str:
        if get_approx_token_count(text) <= self.limit_len:
            return text
        else:
            raw_text_list = self.spliter.split_text(text)
            sum_text_list = []
            for raw_text in raw_text_list:
                prompt = f"""Please summarize the following text: {raw_text}"""
                out = self.llm.run(prompt)
                logger.info(f"single recursive summarization call from {len(raw_text)} to {len(out)} characters")
                sum_text_list.append(out)
            return "\n".join(sum_text_list)

    def run(self, text: str, tag: str = "") -> str:
        n = get_approx_token_count(text)
        if n <= self.limit_len:
            return text
        else:
            logger.warning(f"Activate recursive summarization on {tag} due to {n} estimated tokens ...")
            sum_text = self._recursive_sum(text)
            sum_n = get_approx_token_count(sum_text)
            logger.warning(f"All recursive summarization on {tag}, tokens from {n} to {sum_n}, len from {len(text)} to {len(sum_text)}")
            return sum_text


class RAGFilter:
    def __init__(self, embedder: LLMAPI, limit_len: int = int(8192 * 0.45), top_k: int = 2):
        self.embedder = embedder
        self.limit_len = limit_len
        self.top_k = top_k
        self.spliter = BaseSplitter(limit_len=self.limit_len)

    def cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        magnitude1 = sum(a ** 2 for a in vec1) ** 0.5
        magnitude2 = sum(b ** 2 for b in vec2) ** 0.5
        return dot_product / (magnitude1 * magnitude2 + 1e-10)

    def rag_filter(self, question: str, content: str) -> str:
        """
        question: short question or instruction
        content: long context to be filtered
        """
        content_list = self.spliter.split_text(content)
        if len(content_list) <= self.top_k:
            return content
        vectors = self.embedder.run_batch(content_list + [question])
        qvec = vectors.pop()
        similarities = [(self.cosine_similarity(qvec, vec), i) for i, vec in enumerate(vectors)]
        similarities = sorted(similarities, reverse=True)[:self.top_k]
        selected_content = "\n".join([content_list[i] for _, i in similarities])
        return selected_content
