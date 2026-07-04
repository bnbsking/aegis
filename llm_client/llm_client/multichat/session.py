from abc import abstractmethod
from typing import Dict, List

from llm_client.llm_calls import LLMAPI
from llm_client.long_context_tools import (
    BaseSummarizer,
    RecursiveSummarizer,
    get_approx_token_count
)
from .memory import ChatSessionState, ChatMemory


class BaseChatSession:
    def chat(self, text: str) -> str:
        raise NotImplementedError
    
    @abstractmethod
    def edit_history_chat(self, history: List[Dict[str, str]]) -> str:
        pass


class ChatSession(BaseChatSession):
    def __init__(
            self,
            llm: LLMAPI,
            limit_len: int,
            summarizer: BaseSummarizer | None = None,
            state: ChatSessionState | None = None
        ):
        self.llm = llm
        self.limit_len = limit_len
        self._summarizer = summarizer or RecursiveSummarizer(llm, limit_len=limit_len // 2)
        self.state = state or ChatSessionState()

    def _get_memory_tokens(self, memory: ChatMemory) -> int:
        combined = memory.summary + " ".join(m["content"] for m in memory.history)
        return get_approx_token_count(combined)

    def _compress_memory(self, memory: ChatMemory) -> ChatMemory:
        mid = max(1, len(memory.history) // 2)
        old_text = "\n".join(
            f"{m['role']}: {m['content']}" for m in memory.history[:mid]
        )
        combined = (memory.summary + "\n" + old_text).strip()
        memory.summary = self._summarizer.run(combined)
        memory.history = memory.history[mid:]
        return memory

    def _generate_title(self, text: str) -> str:
        prompt = f"Generate a concise title for the following conversation:\n{text}"
        title = self.llm.run([{"role": "user", "content": prompt}])
        return title.strip().strip('"')

    def chat(self, text: str) -> str:
        if not self.state.title:  # first turn chat only
            self.state.title = self._generate_title(text)

        self.state.memory.history.append({"role": "user", "content": text})
        self.state.full_history.append({"role": "user", "content": text})
        
        while self._get_memory_tokens(self.state.memory) > self.limit_len:
            self.state.memory = self._compress_memory(self.state.memory)

        if self.state.memory.summary:
            messages = [
                {
                    "role": "system",
                    "content": f"Summary of earlier conversation:\n{self.state.memory.summary}"
                }
            ]
        else:
            messages = []
        messages.extend(self.state.memory.history)

        response = self.llm.run(messages)
        self.state.memory.history.append({"role": "assistant", "content": str(response)})
        self.state.full_history.append({"role": "assistant", "content": str(response)})
        return response

    def edit_history_chat(self, history: List[Dict[str, str]]) -> str:
        text = history.pop()["content"]
        self.state.memory.history = list(history)
        self.state.full_history = list(history)
        out = self.chat(text)
        return out
    
    def edit_title(self, new_title: str):
        self.state.title = new_title
