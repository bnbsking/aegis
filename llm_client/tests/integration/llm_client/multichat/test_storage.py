from pathlib import Path
from tempfile import TemporaryDirectory

from llm_client.multichat.memory import ChatMemory, ChatSessionState
from llm_client.multichat.storage import JsonChatStorage


class TestJsonChatStorage:
    def __init__(self):
        self.tmp_dir = TemporaryDirectory()  # e.g. /tmp/tmpabcd1234
        self.storage = JsonChatStorage(base_dir=Path(self.tmp_dir.name))
        self.account_id = "acct_001"

    def test_load_missing_returns_empty_state(self):
        state = self.storage.load(self.account_id, "does_not_exist")
        assert state.memory.history == []
        assert state.memory.summary == ""
        assert state.full_history == []
        assert state.title == ""
        print("load missing session -> empty ChatSessionState OK")

    def test_save_and_load_roundtrip(self):
        state = ChatSessionState(
            memory=ChatMemory(history=[{"role": "user", "content": "hi"}], summary="old summary"),
            full_history=[
                {"role": "user", "content": "hi"},
                {"role": "assistant", "content": "hello"},
            ],
            title="greeting chat",
        )
        self.storage.save(self.account_id, "sess_roundtrip", state)
        loaded = self.storage.load(self.account_id, "sess_roundtrip")

        assert loaded.memory.history == state.memory.history
        assert loaded.memory.summary == state.memory.summary
        assert loaded.full_history == state.full_history
        assert loaded.title == state.title
        print("save/load roundtrip OK")

    def test_list_session_id_title(self):
        self.storage.save(self.account_id, "sess_a", ChatSessionState(title="chat A"))
        self.storage.save(self.account_id, "sess_b", ChatSessionState(title="chat B"))

        result = dict(self.storage.list_session_id_title(self.account_id))
        assert result["sess_a"] == "chat A"
        assert result["sess_b"] == "chat B"
        print(f"list_session_id_title -> {result}")

    def test_list_session_id_title_unknown_account(self):
        result = self.storage.list_session_id_title("no_such_account")
        assert result == []
        print("list_session_id_title on unknown account -> [] OK")

    def test_delete(self):
        self.storage.save(self.account_id, "sess_to_delete", ChatSessionState(title="temp"))
        self.storage.delete(self.account_id, "sess_to_delete")

        remaining = [sid for sid, _ in self.storage.list_session_id_title(self.account_id)]
        assert "sess_to_delete" not in remaining
        print("delete OK")

    def test_delete_missing_is_noop(self):
        self.storage.delete(self.account_id, "never_existed")  # should not raise
        print("delete missing session -> no-op OK")


if __name__ == "__main__":
    test = TestJsonChatStorage()
    test.test_load_missing_returns_empty_state()
    test.test_save_and_load_roundtrip()
    test.test_list_session_id_title()
    test.test_list_session_id_title_unknown_account()
    test.test_delete()
    test.test_delete_missing_is_noop()
    print("All storage tests passed :D")
