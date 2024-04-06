import asyncio
import json

import dotenv
import streamlit as st
import os
import adaptors
from jinja2 import Environment, PackageLoader, select_autoescape
import psycopg2

dotenv.load_dotenv(f"{os.environ['PROJECT_ROOT']}/.env")
cfg = dotenv.dotenv_values()

db_conn =  psycopg2.connect(f"host={cfg['DB_HOST']} dbname={cfg['DB_NAME']} user={cfg['DB_USER']} password={cfg['DB_PASSWORD']}")

env = Environment(
    loader=PackageLoader("css2_llm_integration", "templates"),
    autoescape=select_autoescape()
)

sales_gen = env.get_template("sales_translate_user_query.txt")
sales_format_response = env.get_template("sales_format_data.txt")
get_question_type = env.get_template("determine_query_kind.txt")


schemas = os.listdir(f"{os.environ['PROJECT_ROOT']}/database_schema")
print(schemas)
all_schemas = []
for schema in schemas:
    with open(f"{os.environ['PROJECT_ROOT']}/database_schema/{schema}", "r") as f:
        all_schemas.append("".join(f.readlines()))

with st.chat_message("robot"):
    st.write("Hello. What is your query? I can answer questions about sales, or I can look at customer reviews for you.")

active_adaptor = adaptors.OpenAIAdaptor()

async def main():
    prompter = st.chat_input("> What is your prompt?")
    while True:
        if prompt := prompter:
            with st.chat_message("user"):
                st.write(prompt)

            question_type_prompt = get_question_type.render(user_prompt=prompt)
            result = await active_adaptor.do_query(question_type_prompt)
            result = result.lower()
            with st.chat_message("robot"):
                st.markdown(f"Based on this query, I think you are asking about: {result}.")

            if "sales" in result:
                with st.chat_message("robot"):
                    try:
                        sales_sql_prompt = sales_gen.render(user_prompt=prompt, db_schema="\n\n".join(all_schemas))
                        sales_sql = await active_adaptor.do_query(sales_sql_prompt, response_json=True)
                        query_json = json.loads(sales_sql)
                        st.json(query_json)
                        with db_conn.cursor() as cur:
                            cur.execute(query_json["query"])
                            results = cur.fetchall()
                        as_json = json.dumps(results, indent=4)
                        st.json(as_json)
                        end_response_prompt = sales_format_response.render(user_prompt=prompt, json=as_json)

                        end_answer = await active_adaptor.do_query(end_response_prompt)

                        st.write(end_answer)
                    except Exception as e:
                        st.write("Something went wrong!")
                        # raising error for debug purposes
                        raise e

                    break
            elif "reviews" in result:
                break
            continue
asyncio.run(main())
