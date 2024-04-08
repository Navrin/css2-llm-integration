import asyncio
import simplejson as json

import dotenv
import streamlit as st
import os
import adaptors
from jinja2 import Environment, PackageLoader, select_autoescape
import psycopg2
from itertools import chain

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
reviews_gen = env.get_template("reviews_pull_data.txt")
reviews_analyse = env.get_template("reviews_analyse_reviews.txt")


schemas = os.listdir(f"{os.environ['PROJECT_ROOT']}/database_schema")
#print(schemas)
all_schemas = []
for schema in schemas:
    with open(f"{os.environ['PROJECT_ROOT']}/database_schema/{schema}", "r") as f:
        all_schemas.append("".join(f.readlines()))


active_adaptor = adaptors.OpenAIAdaptor()
if "messages" not in st.session_state:
    st.session_state.messages = []
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
if "set" not in st.session_state:

    st.set_page_config(layout="wide")
    st.session_state.set = True

async def main():
    chat_col, input_col = st.columns(2)

    # TODO: separate this code into an API and the UI.
    with db_conn.cursor() as cur:
        cur.execute("SELECT name FROM product")
        product_query = cur.fetchall()
        products = list(chain(*product_query))
    with input_col:
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
    with chat_col:
        with st.chat_message("robot"):
            st.write(
                "Hello. What is your query? I can answer questions about sales, or I can look at customer reviews for you.")

        prompter = st.chat_input("> What is your prompt?")
        if prompt := prompter:
            with st.chat_message("user"):
                st.write(prompt)
            st.session_state.messages.append({"role": "user", "content": prompt})

            question_type_prompt = get_question_type.render(user_prompt=prompt)
            result = await active_adaptor.do_query(question_type_prompt, history=st.session_state.messages)
            result = result.lower()
            with st.chat_message("assistant"):
                ai_msg = f"Based on this query, I think you are asking about: {result}."
                st.markdown(ai_msg)
                st.session_state.messages.append({"role": "assistant", "content": ai_msg})



            if "sales" in result:
                with st.chat_message("assistant"):
                    try:
                        sales_sql_prompt = sales_gen.render(user_prompt=prompt, db_schema="\n\n".join(all_schemas))
                        sales_sql = await active_adaptor.do_query(
                            sales_sql_prompt,
                            response_json=True,
                            history=st.session_state.messages
                        )
                        query_json = json.loads(sales_sql)
                        st.json(query_json)
                        with db_conn.cursor() as cur:
                            cur.execute(query_json["query"])
                            results = cur.fetchall()
                        as_json = json.dumps(results, indent=4)
                        st.json(as_json)
                        end_response_prompt = sales_format_response.render(user_prompt=prompt, json=as_json)

                        end_answer = await active_adaptor.do_query(end_response_prompt, history=st.session_state.messages)
                        st.session_state.messages.append({"role": "assistant", "content": end_answer})


                        st.write(end_answer)
                    except Exception as e:
                        st.write("Something went wrong!")
                        # raising error for debug purposes
                        raise e

            elif "reviews" in result:
                with st.chat_message("assistant"):
                    try:
                        reviews_sql_prompt = reviews_gen.render(user_prompt=prompt, db_schema="\n\n".join(all_schemas))
                        reviews_sql = await active_adaptor.do_query(
                            reviews_sql_prompt,
                            response_json=True,
                            history=st.session_state.messages
                        )
                        query_json = json.loads(reviews_sql)
                        st.json(query_json)
                        with db_conn.cursor() as cur:
                            cur.execute(query_json["query"])
                            results = cur.fetchall()
                        as_json = json.dumps(results, indent=4)
                        # st.json(as_json)
                        end_response_prompt = reviews_analyse.render(user_prompt=prompt, reviews=as_json)

                        end_answer = await active_adaptor.do_query(
                            end_response_prompt,
                            history=st.session_state.messages
                        )
                        st.session_state.messages.append({"role": "assistant", "content": end_answer})

                        st.write(end_answer)
                    except Exception as e:
                        st.write("Something went wrong!")
                        # raising error for debug purposes
                        raise e
asyncio.run(main())
