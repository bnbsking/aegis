import uuid
from typing import Dict, List, Tuple

from .memory import ChatSessionState
from .session import BaseChatSession, ChatSession
from .storage import BaseChatStorage, JsonChatStorage


class ChatManager:
    """
    給 server/前端 使用的高階入口, 每個 account_id 底下可以有多個 session_id (如 GPT UI 的左側對話清單)。
    這個 class 不常駐任何 session 狀態, 每次呼叫都會從 storage load/save,
    因此可以直接被 FastAPI 這種 stateless 的 request handler 呼叫。
    """
    def __init__(
            self,
            session_cls: type[BaseChatSession] | None = None,
            session_args: Dict = None,  # llm: LLMAPI, limit_len: int, summarizer: BaseSummarizer
            storage: BaseChatStorage | None = None,
        ):
        self.session_cls = session_cls or ChatSession
        self.session_args = session_args or {}
        self.storage = storage or JsonChatStorage()

    def list_session_id_title(self, account_id: str) -> List[Tuple[str, str]]:
        """列出某帳號底下所有 session_id 及其標題, 給前端顯示側邊欄"""
        return self.storage.list_session_id_title(account_id)

    def delete_session(self, account_id: str, session_id: str) -> None:
        self.storage.delete(account_id, session_id)

    def get_full_history(self, account_id: str, session_id: str) -> List[Dict[str, str]]:
        """點擊某則對話, 給前端顯示完整對話"""
        session_state = self.storage.load(account_id, session_id)
        return session_state.full_history

    def create_session(self, account_id: str) -> str:
        """建立新對話, 回傳 session_id 給前端"""
        session_id = uuid.uuid4().hex[:12]
        self.storage.save(account_id, session_id, ChatSessionState())
        return session_id

    def chat(self, account_id: str, session_id: str, text: str) -> str:
        """送出一句話並取得回覆, 會自動 load/save 該 session 的狀態"""
        session_state = self.storage.load(account_id, session_id)
        session = self.session_cls(
            state=session_state,
            **self.session_args
        )
        
        response = session.chat(text)
        self.storage.save(account_id, session_id, session.state)
        return response

    def edit_and_regenerate(
            self, account_id: str, session_id: str, history: List[Dict[str, str]]
        ) -> str:
        """
        編輯歷史中某一則 user 訊息並重新產生回覆, 該訊息之後的對話會被捨棄。
        history: 完整對話, 最後一筆為編輯後的 user 訊息, 之前的訊息維持不變。
        """
        session_state = self.storage.load(account_id, session_id)
        session = self.session_cls(
            state=session_state,
            **self.session_args
        )
        response = session.edit_history_chat(list(history))
        self.storage.save(account_id, session_id, session.state)
        return response
    
    def edit_title(self, account_id: str, session_id: str, new_title: str) -> None:
        """編輯對話標題"""
        session_state = self.storage.load(account_id, session_id)
        session_state.title = new_title
        self.storage.save(account_id, session_id, session_state)
