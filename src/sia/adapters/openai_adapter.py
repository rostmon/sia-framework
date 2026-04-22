"""
OpenAIAdapter — wraps OpenAI Chat Completions API with Async support.

Install:  pip install sia-framework[openai]
          (or: pip install openai>=1.0)

Requires: OPENAI_API_KEY environment variable.
"""
import os
import math
from typing import Optional
from sia.adapters.base import ModelAdapter, ModelResponse


class OpenAIAdapter(ModelAdapter):
    """
    SIA-compatible adapter for OpenAI Chat Completions.
    Supports both sync (generate) and async (agenerate).
    """

    def __init__(self, model: str = "gpt-4o", api_key: str | None = None):
        self._model = model
        self._api_key = api_key or os.getenv("OPENAI_API_KEY")

    @property
    def provider_name(self) -> str:
        return "openai"

    def _process_response(self, raw) -> ModelResponse:
        content = raw.choices[0].message.content or ""
        confidence = 0.85
        try:
            logprob = raw.choices[0].logprobs.content[0].logprob
            confidence = min(1.0, max(0.0, math.exp(logprob)))
        except (AttributeError, IndexError, TypeError):
            pass

        return ModelResponse(
            content=content,
            confidence=confidence,
            rag_verified=False,
            provider=self.provider_name,
            raw=raw.model_dump(),
        )

    def generate(self, prompt: str, **kwargs) -> ModelResponse:
        try:
            from openai import OpenAI
        except ImportError:
            raise ImportError("OpenAI SDK not installed. Run: pip install openai>=1.0")

        client = OpenAI(api_key=self._api_key)
        raw = client.chat.completions.create(
            model=self._model,
            messages=[{"role": "user", "content": prompt}],
            logprobs=True,
            top_logprobs=1,
            **kwargs,
        )
        return self._process_response(raw)

    async def agenerate(self, prompt: str, **kwargs) -> ModelResponse:
        try:
            from openai import AsyncOpenAI
        except ImportError:
            raise ImportError("OpenAI SDK not installed. Run: pip install openai>=1.0")

        client = AsyncOpenAI(api_key=self._api_key)
        raw = await client.chat.completions.create(
            model=self._model,
            messages=[{"role": "user", "content": prompt}],
            logprobs=True,
            top_logprobs=1,
            **kwargs,
        )
        return self._process_response(raw)

    async def astream(self, prompt: str, **kwargs):
        try:
            from openai import AsyncOpenAI
        except ImportError:
            raise ImportError("OpenAI SDK not installed. Run: pip install openai>=1.0")

        client = AsyncOpenAI(api_key=self._api_key)
        stream = await client.chat.completions.create(
            model=self._model,
            messages=[{"role": "user", "content": prompt}],
            stream=True,
            **kwargs,
        )
        async for chunk in stream:
            content = chunk.choices[0].delta.content
            if content is not None:
                yield content
