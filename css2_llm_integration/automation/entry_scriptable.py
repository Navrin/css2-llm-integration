import argparse
import hashlib
import typing
import asyncio
from argparse import ArgumentParser
from io import StringIO

import simplejson as json

import dotenv
import os
# import css2_llm_integration.adaptors.openai_adaptor

import psycopg
from itertools import chain

import toml
from streamlit.runtime.uploaded_file_manager import UploadedFile

parser = ArgumentParser(
    prog="CSS LLM Pipeline",
    description="Responsible for automated testing of LLM models",
)

parser.add_argument('config', metavar="CONFIG_FILE", type=str, help="Path to the testing configuration file.")
parser.add_argument("--env-file", dest="env_file", metavar="ENV_FILE", type=str, help="Path to the .env file.", default=argparse.SUPPRESS)
parser.add_argument("--output-dir", dest="output_dir", metavar="OUTPUT_DIR", type=str, help="Path to the output directory.", default="../out")

async def main(args):
    from css2_llm_integration.automation.Experiment import Experiment
    from css2_llm_integration.automation.experiment_config import ExperimentConfig
    from css2_llm_integration.data_layer import DBContextManager
    from css2_llm_integration.data_layer.DBContextManager import ContextManager
    from css2_llm_integration.data_layer.tool_calling import ToolProvider

    env_cfg = dotenv.dotenv_values()
    db_conn = await psycopg.AsyncConnection.connect(f"host={env_cfg['DB_HOST']} dbname={env_cfg['DB_NAME']} user={env_cfg['DB_USER']} password={env_cfg['DB_PASSWORD']}")
    db_manager = ContextManager(db_conn)
    tool_provider = ToolProvider(db_conn)

    # if "config_as_file" in dir(args):
    #     cfg_file: UploadedFile = args.config_as_file
    #     hash = hashlib.md5(cfg_file.getvalue(), usedforsecurity=False)
    #     stringio = StringIO(cfg_file.getvalue().decode("utf-8"))
    #     cfg_load = toml.loads(stringio.read())
    #
    # else:

    hash = hashlib.md5(open(args.config, "rb").read(), usedforsecurity=False)
    cfg_load = toml.loads(open(args.config, "r").read())
    experiment_cfg = ExperimentConfig(**cfg_load)

    experiment = Experiment(experiment_cfg, db_manager, tool_provider, hashed=hash.hexdigest())

    results = await experiment.run_all(args)
    return results

if __name__ == "__main__":
    parsed_args = parser.parse_args()
    env_path = parsed_args.env_file \
        if "env_file" in parsed_args \
        else f"{os.environ['PROJECT_ROOT']}/.env"

    dotenv.load_dotenv(env_path)

    asyncio.run(main(parsed_args))
