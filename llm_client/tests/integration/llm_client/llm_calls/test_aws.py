import os
import yaml

from llm_client.async_funcs import async_executor
from llm_client.llm_calls import init_model


with open("/app/cfgs/cfg.yaml", "r") as f:
    cfg = yaml.safe_load(f)
llm_chat_cfg = cfg["llm_chat_cfg"]


class TestAWSChatAPI:
    def __init__(self):
        self.llm = init_model(llm_chat_cfg["aws"])

    def test_run(self):
        out = self.llm.run("How are you")
        print(out)
        # I'm doing great, thank you! How can I assist you today?
    
    def test_run_multi_turn(self):
        out = self.llm.run(
            [
                {"role": "user", "content": [{"text": "My name is John. How are you?"}]},
                {"role": "assistant", "content": [{"text": "I'm doing great, thank you! How can I assist you today?"}]},
                {"role": "user", "content": [{"text": "What is my name?"}]}
            ]
        )
        print(out)
        # Your name is John. You told me that at the start of our conversation.

    def test_run_pydantic(self):
        json_schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer"},
                "hobbies": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["name", "hobbies"]
        }
        out = self.llm.run(
            "Generate a fake person information",
            response_format=json_schema
        )
        print(out)
        # {'name': 'Alex Morgan', 'age': 28, 'hobbies': ['reading', 'hiking', 'photography', 'cooking']}

    def test_run_img(self):
        text = "What's in this picture?"
        img_path = "/app/tests/integration/llm_client/llm_calls/dog.jpg"

        image_bytes = open(img_path, "rb").read()
        out = self.llm.run(
            prompt=[
                {
                    "role": "user",
                    "content": [
                        {"image": {"format": "jpeg", "source": {"bytes": image_bytes}}},
                        {"text": text},
                    ]
                }
            ]
        )
        print(out)
        """
        # Picture Description
        This image shows a **Border Collie** dog sitting on a light-colored floor in front of a modern building. The dog has the characteristic Border Collie markings:

        - **Black and white coat** with distinct coloring
        - **Alert, intelligent expression** with bright eyes
        - **Tongue out** in a friendly, happy manner
        - **Pointed ears** standing upright

        The setting appears to be a contemporary outdoor or semi-outdoor space with:
        - A gray pillar or column in the background
        - Modern glass windows/storefront
        - Clean, minimalist architecture
        - What appears to be a public or commercial area

        The dog is sitting in a well-behaved pose and appears to be a professional or posed photograph, likely for promotional or portfolio purposes
        """

    def test_run_pdf(self):
        text = "請幫我總結這份 PDF 的內容。"
        pdf_path = "/app/tests/integration/llm_client/llm_calls/dog.pdf"

        pdf_bytes = open(pdf_path, "rb").read()
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "document": {
                            "format": "pdf",
                            "name": os.path.splitext(os.path.basename(pdf_path))[0],
                            "source": {
                                "bytes": pdf_bytes,
                            },
                        }
                    },
                    {
                        "text": text,
                    },
                ],
            }
        ]
        out = self.llm.run(prompt=messages)
        print(out)
        """
        # PDF 內容總結
        這份 PDF 文件包含以下內容：

        1. **標題**：「This is a border collie」（這是一隻邊境牧羊犬）

        2. **圖片**：展示了一隻黑白相間的邊境牧羊犬，坐在室外白色地面上。該犬具有典型的邊境牧羊犬特徵：
        - 黑白相間的毛色
        - 豎立的耳朵
        - 友善的表情

        3. **說明文字**：
        - 重申「This is a border collie」（這是一隻邊境牧羊犬）
        - 補充說明「This is not a corgi」（這不是一隻柯基犬）

        **主要目的**：該文件似乎是用來區分邊境牧羊犬和柯基犬這兩個不同犬種的簡單教育性資料。
        """

    def test_arun(self):
        out = async_executor(
            self.llm.arun,
            [
                {"prompt": "What is the next day of Sunday?"},
                {"prompt": "How much is 15 * 12"}
            ]
        )
        print(out)
        # ['The next day of Sunday is **Monday**.', '15 * 12 = 180']


if __name__ == "__main__":
    obj = TestAWSChatAPI()
    obj.test_run()
    obj.test_run_multi_turn()
    obj.test_run_pydantic()
    obj.test_run_img()
    obj.test_run_pdf()
    obj.test_arun()
