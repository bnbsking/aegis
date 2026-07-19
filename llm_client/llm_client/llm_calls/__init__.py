import importlib
import traceback
from typing import Any, Dict

from pydantic import BaseModel

from .base import LLMAPI


class LLMConfig(BaseModel):
    mod_name: str
    cls_name: str
    args: Dict[str, Any] = {}


def init_model(cfg_dict: Dict[str, Any]) -> LLMAPI:
    cfg = LLMConfig(**cfg_dict)
    try:
        module = importlib.import_module(f".{cfg.mod_name}", package=__package__)
        cls = getattr(module, cfg.cls_name)
        return cls(**cfg.args)
    except Exception as e:
        raise ValueError(f"無法載入模組或類別 {cfg.mod_name}.{cfg.cls_name}: {traceback.format_exc()}, e={e}")
