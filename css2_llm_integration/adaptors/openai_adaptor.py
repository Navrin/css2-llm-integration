from css2_llm_integration.llm_adaptor import LLMAdaptor
from dotenv import dotenv_values
from openai import AsyncOpenAI

import os

class OpenAIAdaptor(LLMAdaptor):
    client: AsyncOpenAI

    def __init__(self, model="gpt-3.5-turbo"):
        config = dotenv_values(f"{os.environ['PROJECT_ROOT']}/.env")
        key = config["OPENAI_KEY"]
        self.model = model
        self.client = AsyncOpenAI(api_key=key)

    async def do_query(self, prompt: str, history=None, response_json = False) -> str:
        if history is None:
            history = []

        response = await self.client.chat.completions.create(
            messages=[
                *history,
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            response_format={"type": "json_object"} if response_json else None,
            model=self.model
        )
        return response.choices[0].message.content
