import json

from css2_llm_integration.adaptors.tool_calling import get_tools_with_schema
from css2_llm_integration.llm_adaptor import LLMAdaptor
from dotenv import dotenv_values
from openai import AsyncOpenAI
from transformers import pipeline

import psycopg2
import os

from css2_llm_integration.templates import all_schemas


class OpenAIAdaptor(LLMAdaptor):
    client: AsyncOpenAI

    def __init__(self, model="gpt-3.5-turbo"):
        cfg = dotenv_values(f"{os.environ['PROJECT_ROOT']}/.env")
        key = cfg["OPENAI_KEY"]
        self.model = model
        self.client = AsyncOpenAI(api_key=key)
        # self.sql_gen = pipeline("text-generation", model="chatdb/natural-sql-7b")
        self.db_conn = psycopg2.connect(
            f"host={cfg['DB_HOST']} dbname={cfg['DB_NAME']} user={cfg['DB_USER']} password={cfg['DB_PASSWORD']}")

    async def do_query(self, prompt: str, history, response_json=False, tool_query_max=5) -> str:

        response = await self.client.chat.completions.create(
            messages=[
                *history,
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            response_format={"type": "json_object"} if response_json else None,
            tools=get_tools_with_schema("\n".join(all_schemas)),
            tool_choice="auto" if tool_query_max > 0 else "none",
            model=self.model
        )
        print(f"response: == {response=}")
        choice = response.choices[0]

        if choice.finish_reason == "tool_calls" and tool_query_max > 0:
            print("doing tool calls!")
            for tool_call in choice.message.tool_calls:
                if tool_call.function.name == "query_database":
                    print(tool_call)
                    question = json.loads(tool_call.function.arguments)["query"]
                    # sql = await self.generate_sql(question)
                    # tmp
                    with self.db_conn.cursor() as cur:
                        cur.execute(question)
                        results = cur.fetchall()

                    history.append({
                        "role": "function",
                        "tool_call_id": tool_call.id,
                        "name": tool_call.function.name,
                        "content": str(results),
                        #"ignore": True,
                    })
            return await self.do_query(prompt, history, response_json, tool_query_max - 1)
        print(history)
        print(response)
        return response.choices[0].message.content

    async def generate_sql(self, prompt: str):
        return self.sql_gen(prompt, return_text=True)
