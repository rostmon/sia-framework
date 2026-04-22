"""
SIA Framework - Model Adapter Registry

Available adapters:
  MockAdapter       - Deterministic mock for testing (no API keys needed)
  OpenAIAdapter     - OpenAI Chat Completions (pip install sia-framework[openai])
  AnthropicAdapter  - Anthropic Claude Messages  (pip install sia-framework[anthropic])
  HuggingFaceAdapter- HuggingFace Inference API  (pip install sia-framework[huggingface])
"""
from sia.adapters.base import ModelAdapter, ModelResponse
from sia.adapters.mock_adapter import MockAdapter

__all__ = ["ModelAdapter", "ModelResponse", "MockAdapter"]
