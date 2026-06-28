from deepagents import create_deep_agent
import yaml

from llm_client.lc.vllm import LangChainVLLM
from llm_client.llm_calls import init_model


cfg = yaml.safe_load(open("/app/cfgs/cfg.yaml", "r"))
llm = init_model(cfg["llm_chat_cfg"]["vllm"])
langchain_vllm = LangChainVLLM(llm=llm)


def get_weather(city: str) -> str:
    """Get weather for a given city."""
    return f"It's always sunny in {city}!"

agent = create_deep_agent(
    model=langchain_vllm,
    tools=[get_weather],
    system_prompt="You are a helpful assistant",
)

agent.invoke(
    {"messages": [{"role": "user", "content": "How's the weather in Taipei?"}]}
)

"""
  File "/root/.cache/pypoetry/virtualenvs/llm-client-9TtSrW0h-py3.12/lib/python3.12/site-packages/langchain_core/language_models/chat_models.py", line 2355, in bind_tools
    raise NotImplementedError
NotImplementedError
During task with name 'model' and id '5098d02a-0f44-0800-a5fe-d36e13c3f5d9'
"""