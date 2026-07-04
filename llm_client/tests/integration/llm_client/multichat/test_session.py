import yaml

from llm_client.llm_calls import init_model
from llm_client.multichat.memory import ChatMemory, ChatSessionState
from llm_client.multichat.session import ChatSession


with open("/app/cfgs/cfg.yaml", "r", encoding="utf-8") as f:
    cfg = yaml.safe_load(f)
llm_chat_cfg = cfg["llm_chat_cfg"]


class TestChatSession:
    def __init__(self):
        self.llm = init_model(llm_chat_cfg["azure_openai"])

    def _new_session(self, limit_len: int = int(8192 * 0.85)) -> ChatSession:
        return ChatSession(llm=self.llm, limit_len=limit_len)

    def test_chat_appends_to_memory_and_full_history(self):
        session = self._new_session()

        out = session.chat("Hello, who are you?")
        assert isinstance(out, str) and len(out) > 0
        assert session.state.memory.history == [
            {"role": "user", "content": "Hello, who are you?"},
            {"role": "assistant", "content": out},
        ]
        assert session.state.full_history == session.state.memory.history
        # must be independent objects, not the same list (regression guard)
        assert session.state.memory.history is not session.state.full_history
        print(f"chat() reply: {out}")

    def test_first_turn_generates_title(self):
        session = self._new_session()
        assert session.state.title == ""

        session.chat("What is the capital of Taiwan?")
        assert session.state.title != ""
        print(f"generated title: {session.state.title}")

        title_before = session.state.title
        session.chat("And what about Japan?")
        assert session.state.title == title_before  # title only generated on first turn

    def test_memory_compression_triggers_on_long_history(self):
        preset_history = [
            {"role": "user", "content": "Teach me about the history of the Roman Empire."},
            {"role": "assistant", "content": "The Roman Empire was one of the largest empires in history, lasting from 27 BC to 476 AD. It was known for its military prowess, architectural achievements, and influential culture."},
            {"role": "user", "content": "Can you explain the fall of the Roman Empire?"},
            {"role": "assistant", "content": "The fall of the Roman Empire was a complex process influenced by various factors, including economic troubles, military defeats, political instability, and invasions by barbarian tribes. The Western Roman Empire officially fell in 476 AD when the last emperor, Romulus Augustulus, was deposed."},
            {"role": "user", "content": "What were some of the key battles that led to the decline of the Roman Empire?"},
            {"role": "assistant", "content": "Some key battles that contributed to the decline of the Roman Empire include the Battle of Adrianople in 378 AD, where the Romans suffered a significant defeat against the Goths, and the Battle of the Catalaunian Plains in 451 AD, where Roman forces fought against Attila the Hun. These battles weakened the empire's military strength and contributed to its eventual collapse."},
            {"role": "user", "content": "How did the Roman Empire's economy contribute to its decline?"},
            {"role": "assistant", "content": "The Roman Empire's economy faced several challenges that contributed to its decline. These included heavy taxation, inflation, reliance on slave labor, and a decline in trade. The empire's vast size made it difficult to manage resources effectively, leading to economic instability and a weakened ability to support its military and infrastructure."},
        ]  # 337 tokens
        state = ChatSessionState(
            memory=ChatMemory(history=list(preset_history), summary=""),
            full_history=list(preset_history),
            title="existing chat",
        )
        session = ChatSession(llm=self.llm, limit_len=300, state=state)

        session.chat("please continue")

        assert session.state.memory.summary != ""
        assert len(session.state.memory.history) < len(session.state.full_history)
        print(f"summary: {session.state.memory.summary[:80]}...")
        print(f"memory.history len={len(session.state.memory.history)}, full_history len={len(session.state.full_history)}")

    def test_edit_history_chat_no_duplicates(self):
        state = ChatSessionState(
            memory=ChatMemory(
                history=[
                    {"role": "user", "content": "hi"},
                    {"role": "assistant", "content": "hello"},
                ],
                summary="",
            ),
            full_history=[
                {"role": "user", "content": "hi"},
                {"role": "assistant", "content": "hello"},
            ],
            title="greeting chat",
        )
        session = ChatSession(llm=self.llm, limit_len=int(8192 * 0.85), state=state)

        edited_history = [{"role": "user", "content": "edited question"}]
        out = session.edit_history_chat(edited_history)

        expected = [
            {"role": "user", "content": "edited question"},
            {"role": "assistant", "content": out},
        ]
        assert session.state.memory.history == expected
        assert session.state.full_history == expected
        assert session.state.memory.history is not session.state.full_history
        print("edit_history_chat produced no duplicate messages OK")


if __name__ == "__main__":
    test = TestChatSession()
    test.test_chat_appends_to_memory_and_full_history()
    test.test_first_turn_generates_title()
    test.test_memory_compression_triggers_on_long_history()
    test.test_edit_history_chat_no_duplicates()
    print("All session tests passed :D")
