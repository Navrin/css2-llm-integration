import dotenv
import streamlit as st
import os
import adaptors
from jinja2 import Environment, PackageLoader, select_autoescape

env = Environment(
    loader=PackageLoader("css2_llm_integration", "templates"),
    autoescape=select_autoescape()
)

sales_gen = env.get_template("sales_translate_user_query.txt")

dotenv.load_dotenv()

schemas = os.listdir("../database_schema")
print(schemas)
all_schemas = []
for schema in schemas:
    with open(f"../database_schema/{schema}", "r") as f:
        all_schemas.append("".join(f.readlines()))

with st.chat_message("robot"):
    st.write("Hello. What is your query? I can answer questions about sales, or I can look at customer reviews for you.")

active_adaptor = adaptors.OpenAIAdaptor()
prompt = st.chat_input("> What is your prompt?")
chat_user = st.chat_message("user")
chat_ai = st.chat_message("robot")

while True:
    if prompt:
        with chat_user:
            st.write(prompt)

        if prompt == "sales":
            with chat_ai:
                st.write(sales_gen.render(user_prompt="What is the best selling product?", db_schema="\n\n".join(all_schemas)))
                break
        elif prompt == "reviews":
            break
        continue
