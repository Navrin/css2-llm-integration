"""
Base class for an LLM adaptor.
"""


class LLMAdaptor:
    name = "Base Adaptor"

    async def do_query(self, prompt: str) -> str:
        raise NotImplementedError
