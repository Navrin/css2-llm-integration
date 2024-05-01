from typing import Optional

from css2_llm_integration.data_layer.tool_calling import ToolProvider
from css2_llm_integration.llm_adaptor import LLMAdaptor
from openai import AsyncOpenAI

import os


class OpenAIAdaptor(LLMAdaptor):
    client: AsyncOpenAI
    tool_provider: ToolProvider

    def __init__(self,
                 tool_provider: ToolProvider,
                 use_openrouter=False, model="openai/gpt-3.5-turbo",
                 seed_all: Optional[int] = None):
        if use_openrouter:
            key = os.getenv("OR_KEY")
            self.client = AsyncOpenAI(
                api_key=key,
                base_url="https://openrouter.ai/api/v1",
            )
        else:
            key = os.getenv("OPENAI_KEY")
            self.client = AsyncOpenAI(api_key=key)
        self.model = model
        self.tool_provider = tool_provider
        self.seed = seed_all

    async def do_query(self, prompt: str, history, response_json=False, tool_query_max=5, is_tool_call=False) -> str:
        if not is_tool_call:
            history.append({
                "role": "user",
                "content": prompt
            })
        response = await self.client.chat.completions.create(
            messages=history,
            response_format={"type": "json_object"} if response_json else None,
            tools=self.tool_provider.generate_tools(),
            tool_choice="auto" if tool_query_max > 0 else "none",
            model=self.model,
            seed=self.seed,
        )
        #print(f"response: == {response=}")
        choice = response.choices[0]


        if choice.finish_reason == "tool_calls" and tool_query_max > 0:
            for tool_call in choice.message.tool_calls:
                history.append(await self.tool_provider.run_tool_call(tool_call))
            return await self.do_query(prompt, history, response_json, tool_query_max - 1, is_tool_call=True)
        # print(history)
        # print(response)
        history.append({
            "role": "assistant",
            "content": choice.message.content
        })
        return response.choices[0].message.content