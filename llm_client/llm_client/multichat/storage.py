from dataclasses import asdict
import json
from pathlib import Path
from typing import Dict, List, Tuple

from .memory import ChatSessionState, ChatMemory


class BaseChatStorage:
    """IO of chat_memory and full_history"""
    def load(self, account_id: str, session_id: str) -> ChatSessionState:
        raise NotImplementedError
    
    def save(self, account_id: str, session_id: str, state: ChatSessionState):
        raise NotImplementedError

    def delete(self, account_id: str, session_id: str):
        raise NotImplementedError
    
    def list_session_id_title(self, account_id: str) -> List[Tuple[str, str]]:
        raise NotImplementedError


class JsonChatStorage(BaseChatStorage):
    """
    storage format
    {
        "memory": {
            "history": [...],
            "summary": "..."
        },
        "full_history": [...],
        "title": "..."
    }
    """
    def __init__(self, base_dir: Path | None = None):
        self.base_dir = base_dir or Path("/app/.chat_storage")

    def _get_state_path(self, account_id: str, session_id: str) -> Path:
        return self.base_dir / account_id / f"{session_id}.json"

    def load(self, account_id: str, session_id: str) -> ChatSessionState:
        path = self._get_state_path(account_id, session_id)
        if not path.exists():
            return ChatSessionState()
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            memory = ChatMemory(**data["memory"])
            full_history = data.get("full_history", [])
            title = data.get("title", "")
            return ChatSessionState(memory=memory, full_history=full_history, title=title)

    def save(self, account_id: str, session_id: str, state: ChatSessionState):
        path = self._get_state_path(account_id, session_id)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(
                {"memory": asdict(state.memory), "full_history": state.full_history, "title": state.title},
                f,
                ensure_ascii=False,
                indent=4
            )

    def delete(self, account_id: str, session_id: str):
        path = self._get_state_path(account_id, session_id)
        if path.exists():
            path.unlink()

    def list_session_id_title(self, account_id: str) -> List[Tuple[str, str]]:
        account_dir = self.base_dir / account_id
        if not account_dir.exists():
            return []
        result = []
        for p in account_dir.glob("*.json"):
            with open(p, "r", encoding="utf-8") as f:
                data = json.load(f)
                title = data.get("title", "")
                result.append((p.stem, title))
        return result
    