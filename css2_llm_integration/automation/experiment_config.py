from typing import List, Optional
from pydantic import BaseModel
class ConfigReviewEntry(BaseModel):
    product_id: int
    review: str
    score: int
    customer_name: Optional[str] = None

class ConfigPromptModifier(BaseModel):
    before_all: Optional[str] = None
    before_prompt: Optional[str] = None
    after_prompt: Optional[str] = None

class RunConfig(BaseModel):
    description: str
    reviews: Optional[List[ConfigReviewEntry]] = []
    prompt_modifier: ConfigPromptModifier = ConfigPromptModifier()

class Prompt(BaseModel):
    query: List[str]


class ExperimentConfig(BaseModel):
    name: str
    models: List[str]
    seed: int

    runs: dict[str, RunConfig]
    prompts: List[Prompt]