import typing as t

from css2_llm_integration.llm_adaptor import LLMAdaptor, HistoryMessage
from css2_llm_integration.templates import *

import simplejson as json
import psycopg2

class ChatSession:
    def get_prompt_history(self):
        # return [msg for msg in self.history if "ignore" not in msg or not msg["ignore"]]
        return self.history

    def __init__(self, model: LLMAdaptor, db, history: t.List[HistoryMessage]):
        self.model = model
        self.db = db
        self.history = history

    async def run_prompt(self, prompt: str):
        # question_type_prompt = get_question_type.render(user_prompt=prompt)
        # result = await self.model.do_query(question_type_prompt, history=self.get_prompt_history())
        # result = result.lower()

        answer = await self.model.do_query(prompt, history=self.get_prompt_history())

        #ai_msg = f"Based on this query, I think you are asking about: {result}."
        #yield ai_msg

        # try:
        #     if "sales" in result:
        #         async for m in self.run_sales_prompt(prompt):
        #             yield m
        #     elif "reviews" in result:
        #         async for m in self.run_reviews_prompt(prompt):
        #             yield m
        # except Exception as e:
        #     raise e
        yield answer

    async def run_sales_prompt(self, prompt: str):
        sales_sql_prompt = sales_gen.render(user_prompt=prompt, db_schema="\n\n".join(all_schemas))
        sales_sql = await self.model.do_query(
            sales_sql_prompt,
            response_json=True,
            history=self.get_prompt_history()
        )
        query_json = json.loads(sales_sql)
        yield query_json

        with self.db.cursor() as cur:
            cur.execute(query_json["query"])
            results = cur.fetchall()
        as_json = json.dumps(results, indent=4)
        yield as_json
        end_response_prompt = sales_format_response.render(user_prompt=prompt, json=as_json)

        end_answer = await self.model.do_query(end_response_prompt, history=self.get_prompt_history())
        yield end_answer

    async def run_reviews_prompt(self, prompt: str):
        reviews_sql_prompt = reviews_gen.render(user_prompt=prompt, db_schema="\n\n".join(all_schemas))
        reviews_sql = await self.model.do_query(
            reviews_sql_prompt,
            response_json=True,
            history=self.get_prompt_history()
        )
        query_json = json.loads(reviews_sql)
        yield query_json

        with self.db.cursor() as cur:
            cur.execute(query_json["query"])
            results = cur.fetchall()
        as_json = json.dumps(results, indent=4)
        yield as_json
        end_response_prompt = reviews_analyse.render(user_prompt=prompt, reviews=as_json)

        end_answer = await self.model.do_query(
            end_response_prompt,
            history=self.get_prompt_history()
        )

        yield end_answer



