"""
HuggingFaceAdapter — wraps HuggingFace Inference API (hosted or local).

Install:  pip install sia-framework[huggingface]
          (or: pip install huggingface-hub>=0.20)

For hosted endpoints, set HF_TOKEN environment variable.
For local pipelines, install: pip install transformers torch
"""
import os
from sia.adapters.base import ModelAdapter, ModelResponse


class HuggingFaceAdapter(ModelAdapter):
    """
    SIA-compatible adapter for HuggingFace models.

    Supports two modes:
    1. Hosted Inference API:
        adapter = HuggingFaceAdapter(model_id="meta-llama/Llama-3.1-8B-Instruct")
    2. Local pipeline:
        adapter = HuggingFaceAdapter(model_id="gpt2", local=True)

    Usage:
        adapter = HuggingFaceAdapter(model_id="meta-llama/Llama-3.1-8B-Instruct")
        client = SIAClient(adapter=adapter, config_path="configs/eu_ai_act_full.yaml")
        response = client.chat("Explain quantum computing.")
    """

    def __init__(self, model_id: str, local: bool = False, token: str | None = None):
        self._model_id = model_id
        self._local = local
        self._token = token or os.getenv("HF_TOKEN")

    @property
    def provider_name(self) -> str:
        return "huggingface"

    def generate(self, prompt: str, **kwargs) -> ModelResponse:
        if self._local:
            return self._generate_local(prompt, **kwargs)
        return self._generate_hosted(prompt, **kwargs)

    def _generate_hosted(self, prompt: str, **kwargs) -> ModelResponse:
        try:
            from huggingface_hub import InferenceClient
        except ImportError:
            raise ImportError(
                "HuggingFace Hub not installed. Run: pip install sia-framework[huggingface]\n"
                "Or: pip install huggingface-hub>=0.20"
            )

        client = InferenceClient(model=self._model_id, token=self._token)
        raw_content = client.text_generation(prompt, max_new_tokens=kwargs.get("max_new_tokens", 512))

        return ModelResponse(
            content=raw_content,
            confidence=0.80,   # HF hosted API does not expose logprobs by default
            rag_verified=False,
            provider=self.provider_name,
            raw={"model_id": self._model_id, "response": raw_content},
        )

    def _generate_local(self, prompt: str, **kwargs) -> ModelResponse:
        try:
            from transformers import pipeline
        except ImportError:
            raise ImportError(
                "Transformers not installed for local mode. Run: pip install transformers torch"
            )

        pipe = pipeline("text-generation", model=self._model_id)
        result = pipe(prompt, max_new_tokens=kwargs.get("max_new_tokens", 256))
        content = result[0].get("generated_text", "")

        return ModelResponse(
            content=content,
            confidence=0.75,   # Local models: no confidence signal; use conservative default
            rag_verified=False,
            provider=f"{self.provider_name}:local",
            raw=result[0],
        )
