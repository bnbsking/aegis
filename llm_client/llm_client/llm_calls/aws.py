from typing import List, Dict

import aioboto3
import boto3

from .base import LLMAPI


class AWSChatAPI(LLMAPI):
    models = [
        "global.anthropic.claude-haiku-4-5-20251001-v1:0",
        "global.anthropic.claude-sonnet-4-6",
        "global.anthropic.claude-opus-4-5-20251101-v1:0"
    ]

    def __init__(
            self,
            profile_name: str = "emc-ai-poc",
            region_name: str = "ap-southeast-1",
            model_name: str = "global.anthropic.claude-haiku-4-5-20251001-v1:0"
        ):
        session = boto3.Session(
            profile_name=profile_name,
            region_name=region_name
        )
        asession = aioboto3.Session(
            profile_name=profile_name,
            region_name=region_name
        )
        self.client = session.client("bedrock-runtime")
        self.asession = asession
        self.model_name = model_name

    def run(
            self,
            prompt: str | List[Dict],
            response_format: Dict = None,
            max_tokens: int = 32768,
            temperature: float = 0.2
        ) -> str | Dict:
        if isinstance(prompt, str):
            prompt = [{"role": "user", "content": [{"text": prompt}]}]

        cfg = {
            "modelId": self.model_name,
            "messages": prompt,
            "inferenceConfig": {
                "maxTokens": max_tokens,
                "temperature": temperature
            }
        }
        if response_format is not None:
            tool_name = "extract_output"
            tool_config = {
                "tools": [
                    {
                        "toolSpec": {
                            "name": tool_name,
                            "description": "Return the result following the required JSON schema.",
                            "inputSchema": {"json": response_format}
                        }
                    }
                ],
                "toolChoice": {"tool": {"name": tool_name}}
            }
            cfg["toolConfig"] = tool_config
        
        response = self.client.converse(**cfg)
        if response_format is None:
            return response["output"]["message"]["content"][0]["text"]
        else:
            return response["output"]["message"]["content"][0]['toolUse']['input']

    async def arun(
            self,
            prompt: str | List[Dict],
            response_format: Dict = None,
            max_tokens: int = 32768,
            temperature: float = 0.2
        ) -> str | Dict:
        if isinstance(prompt, str):
            prompt = [{"role": "user", "content": [{"text": prompt}]}]

        cfg = {
            "modelId": self.model_name,
            "messages": prompt,
            "inferenceConfig": {
                "maxTokens": max_tokens,
                "temperature": temperature
            }
        }
        if response_format is not None:
            tool_name = "extract_output"
            tool_config = {
                "tools": [
                    {
                        "toolSpec": {
                            "name": tool_name,
                            "description": "Return the result following the required JSON schema.",
                            "inputSchema": {"json": response_format}
                        }
                    }
                ],
                "toolChoice": {"tool": {"name": tool_name}}
            }
            cfg["toolConfig"] = tool_config

        async with self.asession.client("bedrock-runtime") as client:
            response = await client.converse(**cfg)
        if response_format is None:
            return response["output"]["message"]["content"][0]["text"]
        else:
            return response["output"]["message"]["content"][0]['toolUse']['input']
        