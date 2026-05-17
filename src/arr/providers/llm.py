"""LLM provider abstraction.

The pipeline talks to LLMs only through `LLMProvider`. The default
implementation routes to OpenRouter, which presents an OpenAI-compatible
chat-completions API and lets us swap providers behind a single base URL.

JSON responses are coerced via `complete_json`: the prompt is instructed to
return valid JSON, the response is parsed, and the result is validated
against a Pydantic model. A single retry is attempted on parse failure with
the parser error appended as context — past two attempts, we surface the
error rather than silently looping.
"""

from __future__ import annotations

import json
from typing import Any, Protocol, TypedDict, TypeVar

import httpx
from pydantic import BaseModel, ValidationError


class Message(TypedDict):
    role: str  # "system" | "user" | "assistant"
    content: str


T = TypeVar("T", bound=BaseModel)


class LLMError(RuntimeError):
    """Raised when the LLM call cannot be satisfied (network, auth, parse)."""


class LLMProvider(Protocol):
    def complete(
        self,
        messages: list[Message],
        model: str,
        *,
        max_tokens: int | None = None,
        temperature: float | None = None,
    ) -> str:
        ...

    def complete_json(
        self,
        messages: list[Message],
        model: str,
        schema: type[T],
        *,
        max_tokens: int | None = None,
        temperature: float | None = None,
    ) -> T:
        ...


_JSON_INSTRUCTION = (
    "Return ONLY a single JSON object that conforms to this schema. No prose, "
    "no code fences, no commentary. JSON schema:\n{schema_json}"
)


class OpenRouterLLM:
    """OpenRouter implementation of LLMProvider.

    Uses the OpenAI-compatible /chat/completions endpoint at
    https://openrouter.ai/api/v1. Model strings should be in OpenRouter's
    namespaced form (e.g. "anthropic/claude-sonnet-4-7").
    """

    def __init__(
        self,
        api_key: str,
        *,
        base_url: str = "https://openrouter.ai/api/v1",
        timeout: float = 60.0,
        http_referer: str = "https://github.com/danielwipert/arr",
        app_name: str = "ARR LinkedIn Drafter",
    ) -> None:
        if not api_key:
            raise LLMError("OpenRouter API key is required")
        self._client = httpx.Client(
            base_url=base_url,
            timeout=timeout,
            headers={
                "Authorization": f"Bearer {api_key}",
                "HTTP-Referer": http_referer,
                "X-Title": app_name,
            },
        )

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> OpenRouterLLM:
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    def complete(
        self,
        messages: list[Message],
        model: str,
        *,
        max_tokens: int | None = None,
        temperature: float | None = None,
    ) -> str:
        payload: dict[str, Any] = {"model": model, "messages": messages}
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens
        if temperature is not None:
            payload["temperature"] = temperature

        try:
            resp = self._client.post("/chat/completions", json=payload)
            resp.raise_for_status()
        except httpx.HTTPError as e:
            raise LLMError(f"OpenRouter request failed: {e}") from e

        data = resp.json()
        try:
            return data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as e:
            raise LLMError(f"Malformed OpenRouter response: {data!r}") from e

    def complete_json(
        self,
        messages: list[Message],
        model: str,
        schema: type[T],
        *,
        max_tokens: int | None = None,
        temperature: float | None = None,
    ) -> T:
        schema_json = json.dumps(schema.model_json_schema(), indent=2)
        instruction: Message = {
            "role": "system",
            "content": _JSON_INSTRUCTION.format(schema_json=schema_json),
        }
        prompt = [instruction, *messages]

        last_error: Exception | None = None
        for attempt in range(2):
            raw = self.complete(prompt, model, max_tokens=max_tokens, temperature=temperature)
            try:
                return schema.model_validate_json(_strip_code_fences(raw))
            except (json.JSONDecodeError, ValidationError) as e:
                last_error = e
                if attempt == 0:
                    prompt = [
                        *prompt,
                        {"role": "assistant", "content": raw},
                        {
                            "role": "user",
                            "content": (
                                "Your last response could not be parsed as JSON matching the "
                                f"schema. Error:\n{e}\n\nReturn a corrected JSON object."
                            ),
                        },
                    ]
        raise LLMError(f"Failed to obtain valid JSON after 2 attempts: {last_error}")


def _strip_code_fences(text: str) -> str:
    """Best-effort cleanup if a model wraps JSON in markdown fences."""
    s = text.strip()
    if s.startswith("```"):
        # Drop opening fence (with optional language tag).
        s = s.split("\n", 1)[1] if "\n" in s else s[3:]
        # Drop trailing fence.
        if s.endswith("```"):
            s = s[: -3]
    return s.strip()
