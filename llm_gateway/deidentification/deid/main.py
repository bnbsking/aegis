from typing import Dict

from deid import deid_collections


class DeidPipeline:
    def __init__(self, deid_cls_name: str, deid_cls_args: Dict):
        deid_cls = getattr(deid_collections, deid_cls_name)
        self.deid_obj = deid_cls(**deid_cls_args)

    def run(self, raw_text: str) -> str:
        if not raw_text:
            return ""
        deid_text = self.deid_obj.deid(raw_text)
        if self.deid_obj.eval(deid_text):
            return deid_text
        else:
            return f"[Deid_failed] {deid_text}"
