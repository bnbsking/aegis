import pandas as pd

from llm_client.long_context_tools import get_approx_token_count


class APIPrice:
    def __init__(self, csv_path: str = "/app/cfgs/price.csv"):
        self.df = pd.read_csv(csv_path)

    def get_price(self, model_name: str, input_text: str, output_text: str) -> float:
        df = self.df[self.df['model'] == model_name]
        if df.empty:
            raise ValueError(f"Price for model '{model_name}' not found.")
        price_in = df['input'].values[0] * get_approx_token_count(input_text) / 1e6
        price_out = df['output'].values[0] * get_approx_token_count(output_text) / 1e6
        return price_in + price_out
