import typing as t
from transformers import pipeline
from css2_llm_integration.llm_adaptor import LLMAdaptor, HistoryMessage


class HFAdaptor(LLMAdaptor):
    def __init__(self, model='openai-community/gpt2-xl', device=-1, batch_size=None):
        self.gen = pipeline('text-generation', model, device=device, batch_size=batch_size, max_new_tokens=300)

    async def do_query(self, prompt: str, history: t.List[HistoryMessage]) -> str:
        messages = [
            *history,
            {
                "role": "user",
                "content": prompt,
            }
        ]
        print(messages)
        output = self.gen(messages)
        print(output)
        output = output[0]['generated_text'][-1]['content']
        return output

