from llm_client.input_converter.response_format import (
    PropertiesResponseFormatConverter,
    PromptHintResponseFormatConverter
)


class TestPropertiesResponseFormatConverter:
    def test_convert(self):
        response_format = {
            "name": "str",
            "age": "int",
            "hobbies": ["str"]
        }

        converter = PropertiesResponseFormatConverter()
        converted_format = converter.convert(response_format)
        assert converted_format == {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer"},
                "hobbies": {"type": "array", "items": {"type": "string"}}
            }
        }


class TestPromptHintResponseFormatConverter:
    def test_convert(self):
        response_format = {
            "name": "str",
            "age": "int",
            "hobbies": ["str"]
        }

        converter = PromptHintResponseFormatConverter()
        converted_format = converter.convert(response_format)
        assert converted_format == """{'name': typing.Optional[str], 'age': typing.Optional[int], 'hobbies': [typing.Optional[str]]}"""


if __name__ == "__main__":
    obj = TestPropertiesResponseFormatConverter()
    obj.test_convert()

    obj2 = TestPromptHintResponseFormatConverter()
    obj2.test_convert()