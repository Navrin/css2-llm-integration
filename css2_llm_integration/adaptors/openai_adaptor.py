from css2_llm_integration.llm_adaptor import LLMAdaptor
from dotenv import dotenv_values
from openai import AsyncOpenAI


class OpenAIAdaptor(LLMAdaptor):
    client: AsyncOpenAI

    def __init__(self, model="gpt-3.5-turbo"):
        config = dotenv_values(".env")
        key = config["OPENAI_KEY"]
        self.model = model
        self.client = AsyncOpenAI(api_key=key)

    async def do_query(self, prompt: str) -> str:
        response = await self.client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            model=self.model
        )
        return response.choices[0].message.content
