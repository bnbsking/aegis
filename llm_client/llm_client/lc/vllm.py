from typing import Dict, List

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from pydantic import ConfigDict
import yaml

from llm_client.llm_calls import init_model
from llm_client.llm_calls.vllm import VLLMChat


class LangChainVLLM(BaseChatModel):
    llm: VLLMChat = None
    model_config = ConfigDict(arbitrary_types_allowed=True)

    def __init__(self, llm: VLLMChat, **kwargs):
        super().__init__(**kwargs)
        self.llm = llm
    
    def messages_convert(self, messages: List[BaseMessage]) -> List[Dict]:
        formatted_messages = []
        for msg in messages:
            # Map LangChain roles to OpenAI/vLLM roles
            if msg.type == "human":
                role = "user"
            elif msg.type == "ai":
                role = "assistant"
            elif msg.type == "system":
                role = "system"
            else:
                role = msg.type # fallback for other types like chat, tool, etc.

            formatted_messages.append({
                "role": role,
                "content": msg.content
            })
        return formatted_messages

    def _generate(self, messages: List[BaseMessage], **kwargs) -> ChatResult:
        formatted_messages = self.messages_convert(messages)
        out = self.llm.run(formatted_messages)
        ai_message = AIMessage(content=out)
        ai_generation = ChatGeneration(message=ai_message)
        return ChatResult(generations=[ai_generation])

    @property
    def _llm_type(self) -> str:
        return "langchain_vllm"


if __name__ == "__main__":
    cfg = yaml.safe_load(open("/app/cfgs/cfg.yaml", "r"))

    llm = init_model(cfg["llm_chat_cfg"]["vllm"])
    langchain_vllm = LangChainVLLM(llm=llm)
    messages = [
        HumanMessage(content="Hello, how are you?")
    ]
    response = langchain_vllm.invoke(messages)
    print(response.content)
