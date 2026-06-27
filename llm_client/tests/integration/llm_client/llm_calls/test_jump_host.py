class TestJumpHostChatAPI:
    def __init__(self):
        self.llm = llm_api.init_model(llm_chat_cfg["jumphost"])

    def test_run(self):
        out = self.llm.run("How are you")
        print(out)

    def test_run_pydantic(self):
        response_format = {
            "name": "str",
            "age": "int",
            "hobbies": ["str"]
        }
        out = self.llm.run(
            "Generate a fake person information",
            response_format,
        )
        print(out)