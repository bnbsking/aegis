import yaml

from llm_client.llm_calls import init_model
from llm_client.price import APIPrice


with open("/app/cfgs/cfg.yaml", "r") as f:
    cfg = yaml.safe_load(f)
    model_cfg = cfg['llm_chat_cfg']['azure_openai']


class TestAPIPrice:
    def test_get_price(self):
        llm = init_model(model_cfg)
        input_text = "Hello, how are you?"
        output_text = llm.run(input_text)
        
        obj = APIPrice()
        price = obj.get_price(model_cfg['args']['model_name'], input_text, output_text)
        print(output_text)
        print(price)  # 3.6400000000000004e-05


if __name__ == "__main__":
    test = TestAPIPrice()
    test.test_get_price()
