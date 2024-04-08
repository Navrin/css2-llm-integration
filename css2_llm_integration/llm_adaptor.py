import typing as t
"""
Base class for an LLM adaptor.
"""

HistoryMessage = t.TypedDict('HistoryMessage', {'role': str, 'content': str})

class LLMAdaptor:
    name = "Base Adaptor"

    async def do_query(self, prompt: str, history: t.List[HistoryMessage]) -> str:
        raise NotImplementedError
