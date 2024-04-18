import asyncio
import simplejson as json

import dotenv
import streamlit as st
import os
import adaptors
import psycopg2
from itertools import chain

from css2_llm_integration.api.api import ChatSession
from templates import *

dotenv.load_dotenv(f"{os.environ['PROJECT_ROOT']}/.env")
cfg = dotenv.dotenv_values()

db_conn =  psycopg2.connect(f"host={cfg['DB_HOST']} dbname={cfg['DB_NAME']} user={cfg['DB_USER']} password={cfg['DB_PASSWORD']}")




# active_adaptor = adaptors.OpenAIAdaptor()
device = -1

if "messages" not in st.session_state:
    st.session_state.messages = []
if "active_adaptor" not in st.session_state:
    st.session_state.active_adaptor = None

if "set" not in st.session_state:

    st.set_page_config(layout="wide")
    st.session_state.set = True

async def main():
    chat_col, input_col = st.columns(2)

    with db_conn.cursor() as cur:
        cur.execute("SELECT name FROM product")
        product_query = cur.fetchall()
        products = list(chain(*product_query))
    with (input_col):
        with st.form(key="review_form"):
            product_select = st.selectbox("Select a product *", products)
            reviewer_name = st.text_input("Enter reviewer name", value=None)
            review_text = st.text_area("Enter review text *", value=None)
            score = st.slider("Select review score *", 1, 5, value=None)
            add_review = st.form_submit_button("Add review")

        if add_review:
            required_list = [product_select, review_text, score]
            any_empty = all(map(lambda x: x is None, required_list))
            if any_empty:
                st.error("At least one of the required fields is empty.")
            else:
                with db_conn.cursor() as cur:
                    add_review = cur.execute("""
                    INSERT INTO product_review (product_id, customer_name, review, rating)
                    VALUES (%s, %s, %s, %s)
                    """,
                         (products.index(product_select)+1, reviewer_name, review_text, score)
                    )
                    db_conn.commit()

        device = st.selectbox("Select device", ["cpu", "cuda:1", "mps"])

        model_choices = {
            "ChatGPT API": lambda: adaptors.OpenAIAdaptor(),
            "GPT2": lambda: adaptors.HFAdaptor(model="openai-community/gpt2-xl", device=device),
            "LLaMa2": lambda: adaptors.HFAdaptor(model="meta-llama/Llama-2-7b-hf", device=device),
            "Hermes-2-Pro-Mistral-7B": lambda: adaptors.HFAdaptor(model="NousResearch/Hermes-2-Pro-Mistral-7B", device=device),
        }
        selected_model = st.selectbox("Select a model", list(model_choices.keys()))
        st.session_state.active_adaptor = model_choices[(selected_model if selected_model is not None else "ChatGPT API")]()

        with st.form(key="batch_prompts"):
            json_text = st.text_area("Enter batch prompt in json", placeholder='{\n "prompts": ["what are my best sellers", "what products need improvement", "what stores sell the most Arctic Freezes" ]\n } ')
            run = st.form_submit_button("Run Batch")

            if run:
                batch = json.loads(json_text)
                prompts = batch["prompts"]
                session = ChatSession(model=st.session_state.active_adaptor, db=db_conn,
                                      history=st.session_state.messages)
                batch_response = []
                for prompt in prompts:
                    st.session_state.messages = []
                    runner = session.run_prompt(prompt)
                    res = []
                    async for n in runner:
                        res.append(n)

                    batch_response.append({
                        "prompt": prompt,
                        "response": res[-1]
                    })
                st.json(batch_response)

    with chat_col:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        with st.chat_message("robot"):
            st.write(
                "Hello. What is your query? I can answer questions about sales, or I can look at customer reviews for you.")

        prompter = st.chat_input("> What is your prompt?")
        if prompt := prompter:
            with st.chat_message("user"):
                st.write(prompt)
            st.session_state.messages.append({"role": "user", "content": prompt, "ignore": True})

            session = ChatSession(model=st.session_state.active_adaptor, db=db_conn, history=st.session_state.messages)
            runner = session.run_prompt(prompt)

            with st.chat_message("assistant"):
                ai_msg = await anext(runner)
                st.markdown(ai_msg)
                st.session_state.messages.append({"role": "assistant", "content": ai_msg})

                try:
                    st.json(await anext(runner))
                    st.json(await anext(runner))
                    end_answer = await anext(runner)
                    st.session_state.messages.append({"role": "assistant", "content": end_answer})

                    st.write(end_answer)
                except Exception as e:
                    st.write("Something went wrong!")
                    # raising error for debug purposes
                    raise e
asyncio.run(main())
