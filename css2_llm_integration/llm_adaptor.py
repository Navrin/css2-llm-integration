import typing as t
"""
Base class for an LLM adaptor.
"""

HistoryMessage = t.TypedDict('HistoryMessage', {'role': str, 'content': str, 'ignore': bool})

class LLMAdaptor:
    name = "Base Adaptor"

    async def do_query(self, prompt: str, history: t.List[HistoryMessage], response_json=False) -> str:
        raise NotImplementedError
