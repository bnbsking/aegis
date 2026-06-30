from typing import Dict

from llm_client.llm_calls import init_model
from llm_client.long_context_tools import BaseSplitter

from deid.cache import LRUCache


class BaseDeid:
    def __init__(self, **kwargs):
        raise NotImplementedError

    def deid(self, raw_text: str, **kwargs) -> str:
        raise NotImplementedError

    def eval(self, deid_text: str, **kwargs) -> bool:
        raise NotImplementedError


class ExampleDeid(BaseDeid):
    """
    Since use local LLM, the following needs to be considered:
    1. cache
    2. long context
    """

    def __init__(
            self,
            splitter_cfg: Dict,
            llm_cfg: Dict,
            deid_prompt_path: str,
            eval_prompt_path: str
        ):
        self.raw2deid_cache = LRUCache(capacity=128)  # raw_text: str -> deid_text: str
        self.deid2eval_cache = LRUCache(capacity=128)  # deid_text: str -> deid_passed: bool
        self.splitter = BaseSplitter(**splitter_cfg)  # for long context
        self.llm = init_model(llm_cfg)
        self.prompt_deid = open(deid_prompt_path, "r").read()
        self.prompt_eval = open(eval_prompt_path, "r").read()
    
    def deid(self, raw_text: str) -> str:
        deid_text = self.raw2deid_cache.get(raw_text)
        if deid_text is not None:
            return deid_text
        
        sub_raw_text_list = self.splitter.split_text(raw_text)
        out_list = []
        for sub_raw_text in sub_raw_text_list:
            prompt = self.prompt_deid.replace("{{ input_text }}", sub_raw_text)
            out = self.llm.run(prompt)
            if isinstance(out, str):
                out = out.strip()
            out_list.append(out)
        deid_text = "\n".join(out_list)
        self.raw2deid_cache.put(raw_text, deid_text)
        return deid_text

    def eval(self, deid_text: str) -> bool:
        deid_passed = self.deid2eval_cache.get(deid_text)
        if deid_passed is not None:
            return deid_passed
        
        sub_deid_text_list = self.splitter.split_text(deid_text)
        deid_passed = True
        for sub_deid_text in sub_deid_text_list:
            prompt = self.prompt_eval.replace("{{ input_text }}", sub_deid_text)
            out = self.llm.run(prompt, response_format='{"has_pii": bool, "explanation": str}')
            deid_passed = isinstance(out, Dict) and "has_pii" in out and not out["has_pii"]
            if not deid_passed:
                print(f"Deid failed\ndeid_text={deid_text}\ndeid_eval={out}")
                break
        self.deid2eval_cache.put(deid_text, deid_passed)
        return deid_passed
        