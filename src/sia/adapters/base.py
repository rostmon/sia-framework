"""
Base adapter contract for SIA Framework.

All third-party model adapters must implement `ModelAdapter` and return
a standardized `ModelResponse`. This decouples the SIA governance engine
from any specific AI provider SDK.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class ModelResponse:
    """Standardized, provider-agnostic response from any AI/ML model."""
    content: str
    confidence: float           # Normalized 0.0–1.0 (from logprobs, metadata, etc.)
    rag_verified: bool = False  # True if output is grounded in cited sources
    provider: str = "unknown"   # "openai" | "anthropic" | "huggingface" | "mock"
    raw: Dict[str, Any] = field(default_factory=dict)  # Raw provider response (forensic)


class ModelAdapter(ABC):
    """
    Abstract base class for all SIA-compatible model adapters.

    Implement `generate()` to wrap any AI/ML provider SDK. SIA's governance
    pipeline calls this after Ingress gates pass and before Egress validation.
    """

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Identifier string for this provider (e.g., 'openai', 'anthropic')."""

    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> ModelResponse:
        """
        Call the underlying model and return a standardized ModelResponse.

        Args:
            prompt: The sanitized, SIA-governed input prompt.
            **kwargs: Provider-specific parameters (temperature, max_tokens, etc.)

        Returns:
            ModelResponse with normalized confidence and raw provider payload.
        """

    @abstractmethod
    async def agenerate(self, prompt: str, **kwargs) -> ModelResponse:
        """Asynchronous version of generate()."""

    @abstractmethod
    async def astream(self, prompt: str, **kwargs):
        """
        Asynchronous streaming version of generate().
        Yields chunks of the response.
        """
        yield
