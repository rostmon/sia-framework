"""
AnthropicAdapter — wraps Anthropic Claude Messages API.

Install:  pip install sia-framework[anthropic]
          (or: pip install anthropic>=0.20)

Requires: ANTHROPIC_API_KEY environment variable.
"""
import os
from sia.adapters.base import ModelAdapter, ModelResponse


class AnthropicAdapter(ModelAdapter):
    """
    SIA-compatible adapter for Anthropic Claude models.

    Supported models: claude-3-5-sonnet-20241022, claude-3-opus-20240229, etc.

    Usage:
        adapter = AnthropicAdapter(model="claude-3-5-sonnet-20241022")
        client = SIAClient(adapter=adapter, config_path="configs/eu_ai_act_full.yaml")
        response = client.chat("Explain quantum computing.")
    """

    # Map Claude stop reasons to approximate confidence scores
    _STOP_REASON_CONFIDENCE = {
        "end_turn": 0.92,
        "max_tokens": 0.65,    # Truncated — treat as lower confidence
        "stop_sequence": 0.88,
    }

    def __init__(self, model: str = "claude-3-5-sonnet-20241022", api_key: str | None = None):
        self._model = model
        self._api_key = api_key or os.getenv("ANTHROPIC_API_KEY")

    @property
    def provider_name(self) -> str:
        return "anthropic"

    def generate(self, prompt: str, **kwargs) -> ModelResponse:
        try:
            import anthropic
        except ImportError:
            raise ImportError(
                "Anthropic SDK not installed. Run: pip install sia-framework[anthropic]\n"
                "Or: pip install anthropic>=0.20"
            )

        if not self._api_key:
            raise EnvironmentError(
                "Missing ANTHROPIC_API_KEY. Set the environment variable or pass api_key= to AnthropicAdapter."
            )

        client = anthropic.Anthropic(api_key=self._api_key)
        raw = client.messages.create(
            model=self._model,
            max_tokens=kwargs.pop("max_tokens", 1024),
            messages=[{"role": "user", "content": prompt}],
            **kwargs,
        )

        content = raw.content[0].text if raw.content else ""
        confidence = self._STOP_REASON_CONFIDENCE.get(raw.stop_reason, 0.80)

        return ModelResponse(
            content=content,
            confidence=confidence,
            rag_verified=False,
            provider=self.provider_name,
            raw=raw.model_dump(),
        )
