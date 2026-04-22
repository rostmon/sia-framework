"""
MockAdapter — deterministic adapter for PoC and unit testing.

No API keys required. Pre-configure the response and confidence at
instantiation time so test scenarios are fully reproducible.
"""
from sia.adapters.base import ModelAdapter, ModelResponse


class MockAdapter(ModelAdapter):
    """
    Deterministic mock adapter for SIA testing pipelines.

    Usage:
        adapter = MockAdapter(
            mock_content="Quantum computers use qubits.",
            mock_confidence=0.95,
            mock_rag_verified=True,
        )
        client = SIAClient(adapter=adapter, ...)
    """

    def __init__(
        self,
        mock_content: str = "Mock LLM response.",
        mock_confidence: float = 0.9,
        mock_rag_verified: bool = True,
    ):
        self._mock_content = mock_content
        self._mock_confidence = mock_confidence
        self._mock_rag_verified = mock_rag_verified

    @property
    def provider_name(self) -> str:
        return "mock"

    def generate(self, prompt: str, **kwargs) -> ModelResponse:
        return ModelResponse(
            content=self._mock_content,
            confidence=self._mock_confidence,
            rag_verified=self._mock_rag_verified,
            provider=self.provider_name,
            raw={"prompt": prompt, "mock": True},
        )
