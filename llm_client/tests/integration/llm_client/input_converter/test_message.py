from llm_client.input_converter.message import OpenAIMessageToAnyMessage
from llm_client.llm_calls.base import img_path_to_openai_url


class TestOpenAIMessageToAnyMessage:
    def test_convert_google(self):
        text = "What's in this picture?"
        img_path = "/app/tests/integration/llm_client/llm_calls/dog.jpg"

        message = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": text},
                    {"type": "image_url", "image_url": {"url": img_path_to_openai_url(img_path)}}
                ]
            }
        ]

        obj = OpenAIMessageToAnyMessage()
        converted_message = obj.convert(message, target="google")
        assert converted_message == [
            {
                "role": "user",
                "parts": [
                    {"text": text},
                    {"inline_data": {"mime_type": "image/jpeg", "data": open(img_path, "rb").read()}}
                ]
            }
        ]

    def test_convert_aws(self):
        text = "What's in this picture?"
        img_path = "/app/tests/integration/llm_client/llm_calls/dog.jpg"

        message = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": text},
                    {"type": "image_url", "image_url": {"url": img_path_to_openai_url(img_path)}}
                ]
            }
        ]

        obj = OpenAIMessageToAnyMessage()
        converted_message = obj.convert(message, target="aws")
        assert converted_message == [
            {
                "role": "user",
                "content": [
                    {"text": text},
                    {"image": {"format": "jpeg", "source": {"bytes": open(img_path, "rb").read()}}}
                ]
            }
        ]


if __name__ == "__main__":
    obj = TestOpenAIMessageToAnyMessage()
    obj.test_convert_google()
    obj.test_convert_aws()