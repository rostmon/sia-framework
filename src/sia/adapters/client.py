"""
SIAClient — unified, plug-and-play compliance orchestrator.

This is the single entry point that makes any AI/ML model EU AI Act compliant.
Replace your existing model call with SIAClient.chat() to apply the full
SIA governance pipeline transparently.

Example (drop-in for OpenAI):
    # Before
    response = openai.chat.completions.create(...)
    content = response.choices[0].message.content

    # After (EU AI Act compliant)
    from sia.adapters import SIAClient
    from sia.adapters.openai_adapter import OpenAIAdapter

    client = SIAClient(
        adapter=OpenAIAdapter(model="gpt-4o"),
        config_path="configs/eu_ai_act_full.yaml",
        environment="prod",
    )
    response = client.chat("Your prompt here")
    print(response.content)         # The governed output
    print(response.trace_hash)      # SHA-256 audit anchor
    print(response.compliant)       # True/False
"""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from sia.adapters.base import ModelAdapter
from sia.core.config import load_logic_gates
from sia.core.engine import RuleEvaluationEngine
from sia.egress.validator import DeterministicEgressValidator
from sia.ingress.orchestrator import ContextualIngressOrchestrator
from sia.traceability.extractor import ReasoningExtractor
from sia.traceability.ledger import AuditLedger


@dataclass
class SIAResponse:
    """
    The governed, compliance-annotated response returned by SIAClient.chat().

    Attributes:
        content:          The actual output text (or block message if intercepted).
        compliant:        Whether the full pipeline passed all governance gates.
        action:           One of "PASSED" | "BLOCKED" | "HUMAN_VETO" | "REWRITTEN".
        article_triggered: EU AI Act article that caused an intervention, if any.
        trace_hash:       SHA-256 anchor to the immutable audit_ledger.jsonl entry.
        provider:         The underlying model provider (e.g., "openai", "mock").
        confidence:       Normalized confidence score from the model (0.0–1.0).
    """
    content: str
    compliant: bool
    action: str                              # "PASSED" | "BLOCKED" | "HUMAN_VETO" | "REWRITTEN"
    article_triggered: Optional[str]
    trace_hash: str
    provider: str
    confidence: float


class SIAClient:
    """
    Plug-and-play EU AI Act compliance wrapper for any AI/ML model.

    Instantiate once, call .chat() anywhere in your existing pipeline.
    """

    def __init__(
        self,
        adapter: ModelAdapter,
        config_path: str | Path = "configs/eu_ai_act_full.yaml",
        environment: str = "prod",
        ledger_path: str = "logs/audit_ledger.jsonl",
    ):
        self._adapter = adapter
        self._config = load_logic_gates(config_path)
        self._engine = RuleEvaluationEngine(self._config, environment=environment)
        self._ingress = ContextualIngressOrchestrator(self._engine)
        self._extractor = ReasoningExtractor()
        self._ledger = AuditLedger(db_path=ledger_path)
        self._egress = DeterministicEgressValidator()

    def chat(self, prompt: str, **model_kwargs) -> SIAResponse:
        """
        Submit a prompt through the full SIA governance pipeline.

        Args:
            prompt:       The user's raw input prompt.
            **model_kwargs: Optional kwargs forwarded to the adapter (temperature, etc.)

        Returns:
            SIAResponse with governed content + compliance metadata.
        """
        # ── 1. INGRESS: Article 5, 10, 14, 15.4 gates ──────────────────────────
        ingress_result = self._ingress.process_prompt(prompt)
        trigger = ingress_result.get("trigger_paragraph")

        # Hard block (Article 5, 10.2f, 15.4)
        if not ingress_result["allowed"]:
            reason = ingress_result.get("reason", "Governance gate blocked execution.")
            hash_ = self._ledger.record_intervention(prompt, trigger, "HTTP_403_FORBIDDEN")
            return SIAResponse(
                content=f"[SIA BLOCKED] {reason}",
                compliant=False,
                action="BLOCKED",
                article_triggered=trigger,
                trace_hash=hash_,
                provider=self._adapter.provider_name,
                confidence=0.0,
            )

        # Soft block: Human Veto required (Article 14.4)
        if ingress_result.get("requires_human_review"):
            hash_ = self._ledger.record_intervention(prompt, trigger, "HTTP_202_ACCEPTED_HUMAN_VETO")
            return SIAResponse(
                content="[SIA HUMAN VETO] This request requires human review before processing.",
                compliant=False,
                action="HUMAN_VETO",
                article_triggered=trigger,
                trace_hash=hash_,
                provider=self._adapter.provider_name,
                confidence=0.0,
            )

        # ── 2. MODEL CALL via pluggable adapter ──────────────────────────────────
        model_response = self._adapter.generate(
            ingress_result["sanitized_prompt"], **model_kwargs
        )

        # ── 3. EGRESS: Article 13, 15.1, 15.3 gates ─────────────────────────────
        is_compliant, governed_output, watermark = self._engine.evaluate_egress(
            model_response.content,
            confidence=model_response.confidence,
            rag_verified=model_response.rag_verified,
        )

        action = "PASSED" if is_compliant else "REWRITTEN"
        if watermark:
            governed_output += f"\n\n[Transparency]: {watermark}"

        # ── 4. TRACEABILITY: Article 12.1 cryptographic trace ───────────────────
        reasoning = self._extractor.extract({"content": model_response.raw.get("reasoning", "")})
        compliance_score = model_response.confidence if is_compliant else 0.0

        hash_ = self._ledger.record_trace(
            prompt=prompt,
            sanitized_prompt=ingress_result["sanitized_prompt"],
            reasoning_path=reasoning,
            output=governed_output,
            compliance_score=compliance_score,
        )

        return SIAResponse(
            content=governed_output,
            compliant=is_compliant,
            action=action,
            article_triggered=None,
            trace_hash=hash_,
            provider=self._adapter.provider_name,
            confidence=model_response.confidence,
        )
