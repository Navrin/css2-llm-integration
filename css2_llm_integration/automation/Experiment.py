import asyncio
import copy
import hashlib
import os
import uuid
from typing import List, Optional

import openai
import simplejson
import streamlit.elements.layouts
from streamlit.elements.lib.mutable_status_container import StatusContainer
from termcolor import colored

from css2_llm_integration.adaptors import OpenAIAdaptor
from css2_llm_integration.automation.experiment_config import ExperimentConfig, ConfigReviewEntry, ConfigPromptModifier, \
    RunConfig
from css2_llm_integration.data_layer import DBContextManager
from css2_llm_integration.data_layer.tool_calling import ToolProvider

def pretty_print_conversation(messages):
    role_to_color = {
        "system": "red",
        "user": "green",
        "assistant": "blue",
        "function": "magenta",
    }

    for message in messages:
        if message["role"] == "system":
            print(colored(f"system: {message['content']}\n", role_to_color[message["role"]]))
        elif message["role"] == "user":
            print(colored(f"user: {message['content']}\n", role_to_color[message["role"]]))
        elif message["role"] == "assistant" and message.get("function_call"):
            print(colored(f"assistant: {message['function_call']}\n", role_to_color[message["role"]]))
        elif message["role"] == "assistant" and not message.get("function_call"):
            print(colored(f"assistant: {message['content']}\n", role_to_color[message["role"]]))
        elif message["role"] == "function":
            print(colored(f"function ({message['name']}): {message['content']}\n", role_to_color[message["role"]]))

class Experiment:
    experiment: ExperimentConfig
    db_manager: DBContextManager
    tool_provider: ToolProvider
    hashed: str

    def __init__(self, experiment: ExperimentConfig, db_manager: DBContextManager, tool_provider: ToolProvider, hashed:str):
        self.experiment = experiment
        self.db_manager = db_manager
        self.tool_provider = tool_provider
        self.hashed = hashed


    async def run_all(
            self,
            args,
            save_output=True,
            write_progress: Optional[StatusContainer] = None
    ):
        output = {}
        output_area = f"{args.output_dir}/run-{self.hashed}"
        if write_progress:
            write_progress.write("Starting Experiment")

        os.makedirs(output_area, exist_ok=True)
        try:
            for run_name, run_cfg in self.experiment.runs.items():
                if write_progress:
                    write_progress.write(f"Starting {run_name}!")
                await self.db_manager.rebuild_db()
                for review in run_cfg.reviews:
                    await self.db_manager.add_review(review)
                if write_progress:
                    write_progress.write(f"Database reinitialisation complete!")

                outcome = await self.run(run_name, run_cfg, write_progress)
                output[run_name] = outcome
            if write_progress:
                write_progress.write("Experiment complete!")

            simplejson.dump(output, open(f"{output_area}/full_run.json", "w"))
            return output
        except Exception as e:
            raise e

    async def run(self, run_name: str, run_cfg: RunConfig, write_progress: Optional[StatusContainer] = None):
        output = {}

        for model_name in self.experiment.models:
            if write_progress:
                write_progress.write(f"Running {run_name} on {model_name}")

            model = OpenAIAdaptor(self.tool_provider,
                                  use_openrouter=not model_name.startswith("openai/"),
                                  model=model_name.lstrip("openai/"),
                                  seed_all=self.experiment.seed)
            history: List[openai.ChatCompletion.HistoryEntry] = []
            output[model_name] = {}
            try:
                for prompts in self.experiment.prompts:
                    if run_cfg.prompt_modifier is not None and run_cfg.prompt_modifier.before_all is not None:
                        history.append({
                            "role": "user",
                            "content": run_cfg.prompt_modifier.before_all,
                        })

                    for prompt in prompts.query:
                        prompt = f'{run_cfg.prompt_modifier.before_prompt or ""}{prompt}{run_cfg.prompt_modifier.after_prompt or ""}'
                        try:
                            await model.do_query(prompt, history)
                            pretty_print_conversation(history)
                        except openai.BadRequestError as e:
                            pretty_print_conversation(history)
                            raise e
                    # should the environment be reset after each prompt run?
                    output[model_name][prompts.query[0]] = copy.deepcopy(history)
                    history = []
            except asyncio.CancelledError:
                return None
        return output
