import openai.types.chat.chat_completion_message_tool_call
import psycopg
from functools import wraps
import simplejson as json

from css2_llm_integration.templates import all_schemas


class ToolDecorator():
    TOOL_DEFAULT = {
        "parameters": {
            "type": "object",
            "properties": {}
        },
        "required": []
    }

    @staticmethod
    def wrapped(f):
        @wraps(f)
        def _impl(*args, **kwargs):
            return f(*args, **kwargs)

        return _impl

    @staticmethod
    def name(name):
        def inner(f):
            if "__tool__" not in dir(f):
                f.__tool__ = ToolDecorator.TOOL_DEFAULT

            f.__tool__['name'] = name
            return ToolDecorator.wrapped(f)

        return inner

    @staticmethod
    def description(description):
        def inner(f):
            if "__tool__" not in dir(f):
                f.__tool__ = ToolDecorator.TOOL_DEFAULT

            f.__tool__['description'] = description
            return ToolDecorator.wrapped(f)

        return inner

    @staticmethod
    def parameter(param, param_type, description_fn, required=False):
        def inner(f):
            if "__tool__" not in dir(f):
                f.__tool__ = ToolDecorator.TOOL_DEFAULT

            f.__tool__['parameters']['properties'][param] = {
                "type": param_type,
                "description": description_fn,
            }

            if required:
                f.__tool__['required'].append(param)
            return ToolDecorator.wrapped(f)

        return inner


tool = ToolDecorator()


def get_schema():
    return "\n".join(all_schemas)


class ToolProvider:
    db_conn: psycopg.AsyncConnection

    def __init__(self, db_conn: psycopg.AsyncConnection):
        self.db_conn = db_conn

    async def run_tool_call(self,
                      tool_call: openai.types.chat.chat_completion_message_tool_call.ChatCompletionMessageToolCall):
        """
        :param tool_call:
        :return: History chat completion object
        """
        target = self.return_method_from_tool_name(tool_call.function.name)
        if target is None:
            raise NotImplementedError("No tool called '{}'".format(tool_call.function.name))

        args = json.loads(tool_call.function.arguments)
        print(f"Performing {tool_call.function.name} with {args=}")
        try:
            response = await target(**args)
        except TypeError as e:
            response = str(e.args[0])

        print(f"Tool call answer {response=}")
        return {
            "role": "function",
            "tool_call_id": tool_call.id,
            "name": tool_call.function.name,
            "content": response
        }

    @tool.name("query_database")
    @tool.description("Executes an postgreSQL query about sales, products, modifiers, stores, and returns the result.")
    @tool.parameter(
        "query",
        "string",
        f"""A valid postgreSQL query extracting info to answer the user's question.
SQL should be written using this database schema:
{get_schema()}
The query should be returned in plain text, not in JSON.""",
        required=True)
    async def query_db(self, query=None):
        # print(f"{'*'*10}Query DB called with {query=}{'*'*10}")
        if query is None:
            raise Exception("No query provided")
        async with self.db_conn.cursor() as cursor:
            try:
                q = await cursor.execute(query)
                results = await cursor.fetchall()
                return str(results)
            except psycopg.DatabaseError as e:
                await cursor.connection.rollback()
                return f'Error {e}'

    def return_method_from_tool_name(self, name):
        methods_with_tools = [method for method in self.__dir__() if "__tool__" in dir(getattr(self, method))]
        for tool_name in methods_with_tools:
            tool = getattr(getattr(self, tool_name), "__tool__")
            if tool["name"] == name:
                return getattr(self, tool_name)
        return None

    def generate_tools(self):
        tools = []
        methods_with_tools = [method for method in self.__dir__() if "__tool__" in dir(getattr(self, method))]

        for tool_name in methods_with_tools:
            tool = getattr(getattr(self, tool_name), "__tool__")

            tools.append({
                "type": "function",
                "function": tool
            })

        return tools
