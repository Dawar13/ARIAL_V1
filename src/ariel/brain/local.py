"""Ollama adapter: the only module that imports the ollama package (the Tier 1 local model)."""

import ollama
from pydantic import BaseModel, ConfigDict

NANOSECONDS = 1e9


class LocalStats(BaseModel):
    """Token counts and timings Ollama reports for one call."""

    model_config = ConfigDict(frozen=True)

    prompt_tokens: int
    output_tokens: int
    load_s: float
    prompt_s: float
    output_s: float
    total_s: float

    @property
    def tokens_per_second(self) -> float:
        return self.output_tokens / self.output_s if self.output_s else 0.0


def installed_models() -> list[str]:
    """Tags of the models Ollama has on disk. Raises ConnectionError if Ollama is not running."""
    return [model.model for model in ollama.list().models if model.model]


def extract[T: BaseModel](
    model: str, prompt: str, schema: type[T], system: str | None = None
) -> tuple[T, LocalStats]:
    """Fill `schema` from `prompt` with the local model, using Ollama structured outputs.

    Thinking is off and temperature is 0, because extraction wants a quick, repeatable answer.
    Raises pydantic.ValidationError if the reply does not match the schema.
    """
    messages = [{"role": "system", "content": system}] if system else []
    messages.append({"role": "user", "content": prompt})
    response = ollama.chat(
        model=model,
        messages=messages,
        format=schema.model_json_schema(),
        think=False,
        options={"temperature": 0},
    )
    result = schema.model_validate_json(response.message.content or "")
    stats = LocalStats(
        prompt_tokens=response.prompt_eval_count or 0,
        output_tokens=response.eval_count or 0,
        load_s=(response.load_duration or 0) / NANOSECONDS,
        prompt_s=(response.prompt_eval_duration or 0) / NANOSECONDS,
        output_s=(response.eval_duration or 0) / NANOSECONDS,
        total_s=(response.total_duration or 0) / NANOSECONDS,
    )
    return result, stats
