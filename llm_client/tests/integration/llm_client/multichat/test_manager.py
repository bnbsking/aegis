from pathlib import Path
from tempfile import TemporaryDirectory

import yaml

from llm_client.llm_calls import init_model
from llm_client.multichat.manager import ChatManager
from llm_client.multichat.storage import JsonChatStorage


with open("/app/cfgs/cfg.yaml", "r", encoding="utf-8") as f:
    cfg = yaml.safe_load(f)
llm_chat_cfg = cfg["llm_chat_cfg"]


class TestChatManager:
    def __init__(self):
        self.llm = init_model(llm_chat_cfg["azure_openai"])
        self.tmp_dir = TemporaryDirectory()
        self.manager = ChatManager(
            session_args={"llm": self.llm, "limit_len": int(8192 * 0.85)},
            storage=JsonChatStorage(base_dir=Path(self.tmp_dir.name)),
        )
        self.account_id = "acct_001"

    def test_create_session_returns_id_and_appears_in_list(self):
        session_id = self.manager.create_session(self.account_id)
        assert session_id != ""

        sessions = dict(self.manager.list_session_id_title(self.account_id))
        assert session_id in sessions
        assert sessions[session_id] == ""  # no title until first chat turn
        print(f"created session: {session_id}")

    def test_chat_persists_full_history_and_title(self):
        session_id = self.manager.create_session(self.account_id)

        reply1 = self.manager.chat(self.account_id, session_id, "Hello, my name is James, who are you?")
        assert isinstance(reply1, str) and len(reply1) > 0

        full_history = self.manager.get_full_history(self.account_id, session_id)
        assert full_history == [
            {"role": "user", "content": "Hello, my name is James, who are you?"},
            {"role": "assistant", "content": reply1},
        ]

        sessions = dict(self.manager.list_session_id_title(self.account_id))
        assert sessions[session_id] != ""  # title generated after first turn
        print(f"title after first turn: {sessions[session_id]}")

        reply2 = self.manager.chat(self.account_id, session_id, "What is my name?")
        full_history = self.manager.get_full_history(self.account_id, session_id)
        assert full_history == [
            {"role": "user", "content": "Hello, my name is James, who are you?"},
            {"role": "assistant", "content": reply1},
            {"role": "user", "content": "What is my name?"},
            {"role": "assistant", "content": reply2},
        ]
        assert "James" in reply2
        print("multi-turn full_history persisted correctly")

    def test_sessions_are_isolated(self):
        session_a = self.manager.create_session(self.account_id)
        session_b = self.manager.create_session(self.account_id)

        self.manager.chat(self.account_id, session_a, "message for session A")
        self.manager.chat(self.account_id, session_b, "message for session B")

        history_a = self.manager.get_full_history(self.account_id, session_a)
        history_b = self.manager.get_full_history(self.account_id, session_b)
        assert history_a[0]["content"] == "message for session A"
        assert history_b[0]["content"] == "message for session B"
        assert len(history_a) == 2
        assert len(history_b) == 2
        print("sessions under the same account are isolated OK")

    def test_edit_and_regenerate_discards_and_replaces_tail(self):
        session_id = self.manager.create_session(self.account_id)
        self.manager.chat(self.account_id, session_id, "hi")

        full_history = self.manager.get_full_history(self.account_id, session_id)
        edited_history = full_history[:-1]  # drop assistant reply
        edited_history[-1] = {"role": "user", "content": "edited question instead of hi"}

        new_reply = self.manager.edit_and_regenerate(self.account_id, session_id, edited_history)

        full_history = self.manager.get_full_history(self.account_id, session_id)
        assert full_history == [
            {"role": "user", "content": "edited question instead of hi"},
            {"role": "assistant", "content": new_reply},
        ]
        print("edit_and_regenerate replaced tail without duplicating messages")

    def test_delete_session_removes_it(self):
        session_id = self.manager.create_session(self.account_id)
        self.manager.chat(self.account_id, session_id, "hello")

        self.manager.delete_session(self.account_id, session_id)

        remaining = dict(self.manager.list_session_id_title(self.account_id))
        assert session_id not in remaining
        assert self.manager.get_full_history(self.account_id, session_id) == []
        print("delete_session OK")


if __name__ == "__main__":
    test = TestChatManager()
    test.test_create_session_returns_id_and_appears_in_list()
    test.test_chat_persists_full_history_and_title()
    test.test_sessions_are_isolated()
    test.test_edit_and_regenerate_discards_and_replaces_tail()
    test.test_delete_session_removes_it()
    print("All manager tests passed :D")
