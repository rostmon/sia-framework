"""
OpenAIAdapter — wraps OpenAI Chat Completions API.

Install:  pip install sia-framework[openai]
          (or: pip install openai>=1.0)

Requires: OPENAI_API_KEY environment variable.
"""
import os
from sia.adapters.base import ModelAdapter, ModelResponse


class OpenAIAdapter(ModelAdapter):
    """
    SIA-compatible adapter for OpenAI Chat Completions.

    Supported models: gpt-4o, gpt-4-turbo, gpt-3.5-turbo, etc.

    Usage:
        adapter = OpenAIAdapter(model="gpt-4o")
        client = SIAClient(adapter=adapter, config_path="configs/eu_ai_act_full.yaml")
        response = client.chat("Explain quantum computing.")
    """

    def __init__(self, model: str = "gpt-4o", api_key: str | None = None):
        self._model = model
        self._api_key = api_key or os.getenv("OPENAI_API_KEY")

    @property
    def provider_name(self) -> str:
        return "openai"

    def generate(self, prompt: str, **kwargs) -> ModelResponse:
        try:
            from openai import OpenAI
        except ImportError:
            raise ImportError(
                "OpenAI SDK not installed. Run: pip install sia-framework[openai]\n"
                "Or: pip install openai>=1.0"
            )

        if not self._api_key:
            raise EnvironmentError(
                "Missing OPENAI_API_KEY. Set the environment variable or pass api_key= to OpenAIAdapter."
            )

        client = OpenAI(api_key=self._api_key)
        raw = client.chat.completions.create(
            model=self._model,
            messages=[{"role": "user", "content": prompt}],
            logprobs=True,
            top_logprobs=1,
            **kwargs,
        )

        content = raw.choices[0].message.content or ""

        # Normalize logprobs to a 0.0–1.0 confidence score
        confidence = 0.85  # default when logprobs unavailable
        try:
            import math
            logprob = raw.choices[0].logprobs.content[0].logprob
            confidence = min(1.0, max(0.0, math.exp(logprob)))
        except (AttributeError, IndexError, TypeError):
            pass

        return ModelResponse(
            content=content,
            confidence=confidence,
            rag_verified=False,   # RAG grounding is external; default False
            provider=self.provider_name,
            raw=raw.model_dump(),
        )
