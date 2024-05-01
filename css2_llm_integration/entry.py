import asyncio
import dataclasses
import typing
import uuid
from io import StringIO

import psycopg
import simplejson as json

import dotenv
import streamlit as st
import os

import toml
from streamlit.runtime.uploaded_file_manager import UploadedFile
from streamlit_modal import Modal

import adaptors
from itertools import chain

from css2_llm_integration.automation.Experiment import Experiment
from css2_llm_integration.automation.experiment_config import ConfigReviewEntry, ExperimentConfig
from css2_llm_integration.data_layer.DBContextManager import ContextManager
from css2_llm_integration.data_layer.tool_calling import ToolProvider
from css2_llm_integration.llm_adaptor import HistoryMessage
from templates import *

dotenv.load_dotenv(f"{os.environ['PROJECT_ROOT']}/.env")
cfg = dotenv.dotenv_values()


# active_adaptor = adaptors.OpenAIAdaptor()
device = -1

if "messages" not in st.session_state:
    st.session_state.messages = []
# if "active_adaptor" not in st.session_state:
#     st.session_state.active_adaptor = None

if "set" not in st.session_state:

    st.set_page_config(layout="wide")
    st.session_state.set = True


@dataclasses.dataclass
class ExperimentConfigArgs:
    env_file: str = None
    output_dir: str = "../out"



async def main():
    db_conn = await psycopg.AsyncConnection.connect(
        f"host={cfg['DB_HOST']} dbname={cfg['DB_NAME']} user={cfg['DB_USER']} password={cfg['DB_PASSWORD']}")

    tool_provider = ToolProvider(db_conn)
    db_manager: ContextManager = ContextManager(db_conn)
    chat_col, input_col = st.columns(2)

    async with db_conn.cursor() as cur:
        await cur.execute("SELECT name FROM product")
        product_query = await cur.fetchall()
        products = list(chain(*product_query))


    with (input_col):
        experiment_config = st.file_uploader("Upload an experiment config file", type=['toml'])
        run_experiment = st.button("Run Experiment using config")

        if run_experiment and experiment_config is not None:
            import css2_llm_integration.automation.entry_scriptable as scriptable
            with st.spinner("Loading config..."):
                stringio = StringIO(experiment_config.getvalue().decode("utf-8"))
                cfg_load = toml.loads(stringio.read())
                experiment_cfg = ExperimentConfig(**cfg_load)

                experiment = Experiment(experiment_cfg, db_manager, tool_provider, hashed=str(uuid.uuid4()))
            cancel_btn = st.button("Cancel Experiment")

            with st.status("Running experiment...", expanded=True) as status:
                runner = asyncio.create_task(experiment.run_all(ExperimentConfigArgs(), write_progress=status))

                while not runner.done():
                    if cancel_btn:
                        runner.cancel()
                        break
                    await asyncio.sleep(0.1)

            st.download_button(
                "Download config output",
                runner.result(),
                "experiment_run.json",
                mime="application/json"
            )


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
                await db_manager.add_review(ConfigReviewEntry(
                    product_id=products.index(product_select)+1,
                    review=review_text,
                    customer_name=reviewer_name,
                    score=score
                ))

        # device = st.selectbox("Select device", ["cpu", "cuda:1", "mps"])

        model_choices = {
            "ChatGPT3.5 API": "openai/gpt-3.5-turbo",
            "GPT4 API": "openai/gpt-4-turbo",
            "LLaMa2": "meta-llama/llama-2-70b-chat",
            "LLaMa3-Instruct": "meta-llama/llama-3-8b-instruct:extended",
            "Nous Hermes 2 Mistral 7B DPO": "nousresearch/nous-hermes-2-mistral-7b-dpo"
        }

        selected_model = st.selectbox("Select a model", list(model_choices.keys()))
        model_name = model_choices[(selected_model if selected_model is not None else model_choices["ChatGPT3.5 API"])]
        active_adaptor = adaptors.OpenAIAdaptor(
            tool_provider,
            model=model_name.lstrip("openai/"),
            use_openrouter=not model_name.startswith("openai/")
        )

        rebuild_db = st.button("Reset and Rebuild DB")
        st.download_button(
            "Export chat",
            json.dumps(st.session_state.messages),
            file_name='chat.json',
            mime='application/json'
        )

        export_prompts = st.button(
            "Export Prompts for Experiment Config",
        )

        prompt_export_msg =\
            f"[[prompts]]\n"\
            f"query = {json.dumps([p['content'] for p in st.session_state.messages if p['role'] == 'user'])}"
        modal = Modal(
            "Prompt entry for the experiment config",
            key="prompt_modal",
        )

        if rebuild_db:
            await db_manager.rebuild_db()

        if export_prompts:
            modal.open()

        if modal.is_open():
            with modal.container():
                st.markdown(f'```\n{prompt_export_msg}\n```')


    with chat_col:
        for message in st.session_state.messages:
            if message["role"] not in ["assistant", "user"]:
                continue

            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        if len(st.session_state.messages) == 0:
            with st.chat_message("robot"):
                st.write(
                    "Hello. What is your query? I can answer questions about sales, or I can look at customer reviews for you.")

        prompter = st.chat_input("> What is your prompt?")
        if prompt_in := prompter:
            with st.chat_message("user"):
                st.write(prompt_in)
            # session = ChatSession(model=active_adaptor, db=db_conn, history=st.session_state.messages)
            # runner = session.run_prompt(prompt_in)

            # st.session_state.messages.append({"role": "user", "content": prompt_in})

            with st.chat_message("assistant"):
                try:
                    end_answer = await active_adaptor.do_query(prompter, st.session_state.messages)
                    # st.session_state.messages.append({"role": "assistant", "content": end_answer})

                    st.write(end_answer)
                except Exception as e:
                    st.write("Something went wrong!")
                    # raising error for debug purposes
                    raise e

asyncio.run(main())
