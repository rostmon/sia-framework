"""
MockAdapter — Deterministic adapter for testing and CI/CD.
"""
from typing import Dict, Optional
from sia.adapters.base import ModelAdapter, ModelResponse


class MockAdapter(ModelAdapter):
    """
    Returns deterministic responses for testing SIA governance gates.
    """

    def __init__(self, mock_content: str = "Mock output.", mock_confidence: float = 0.95, mock_rag_verified: bool = False):
        self.mock_content = mock_content
        self.mock_confidence = mock_confidence
        self.mock_rag_verified = mock_rag_verified

    @property
    def provider_name(self) -> str:
        return "mock"

    def generate(self, prompt: str, **kwargs) -> ModelResponse:
        return ModelResponse(
            content=self.mock_content,
            confidence=self.mock_confidence,
            rag_verified=self.mock_rag_verified,
            provider=self.provider_name,
            raw={"status": "mocked", "reasoning": "Mocked reasoning for traceability."}
        )

    async def agenerate(self, prompt: str, **kwargs) -> ModelResponse:
        import asyncio
        await asyncio.sleep(0.01)  # Simulate network latency
        return self.generate(prompt, **kwargs)
