from dataclasses import dataclass, field  # serialize: asdict(obj); deserialize: cls(**data)
from typing import Dict, List


@dataclass
class ChatMemory:
    """
    responsible for ChatSession to do memorization and summarization. 
    + history: 最近完整對話, 若與summary合計超過token limit 才會壓縮成 summary
    + summary: 較舊的對話, 已被壓縮
    """
    history: List[Dict[str, str]] = field(default_factory=list)
    summary: str = ""


@dataclass
class ChatSessionState:
    """
    responsible for ChatStorage save/load.
    """
    memory: ChatMemory = field(default_factory=ChatMemory)
    full_history: List[Dict[str, str]] = field(default_factory=list)
    title: str = ""
