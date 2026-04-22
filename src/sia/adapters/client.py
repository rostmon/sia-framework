"""
SIAClient — updated to handle new engine signature (4-tuple egress return).
"""
from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Optional

from sia.adapters.base import ModelAdapter
from sia.core.config import load_logic_gates
from sia.core.engine import RuleEvaluationEngine
from sia.egress.validator import DeterministicEgressValidator
from sia.ingress.orchestrator import ContextualIngressOrchestrator
from sia.traceability.extractor import ReasoningExtractor
from sia.traceability.ledger import AuditLedger


@dataclass
class SIAResponse:
    """Governed, compliance-annotated response from SIAClient.chat()."""
    content: str
    compliant: bool
    action: str                              # PASSED | BLOCKED | HUMAN_VETO | REWRITTEN
    article_triggered: Optional[str]
    trace_hash: str
    provider: str
    confidence: float
    http_status: int                         # Standard HTTP code reflecting governance outcome
    http_headers: Dict[str, str] = field(default_factory=dict)  # e.g. X-SIA-AI-Generated


class SIAClient:
    """Plug-and-play EU AI Act compliance wrapper for any AI/ML model."""

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

    def chat(self, prompt: str, rag_metadata: Optional[Dict] = None, **model_kwargs) -> SIAResponse:
        """
        Submit a prompt through the full SIA governance pipeline.

        Args:
            prompt:       The user's raw input prompt.
            rag_metadata: Optional dict from the RAG layer:
                          {"document_id": "...", "source_domain": "internal_kb"}
            **model_kwargs: Forwarded to the adapter (temperature, max_tokens, etc.)
        """
        # ── 1. INGRESS ──────────────────────────────────────────────────────
        ingress_result = self._ingress.process_prompt(prompt)
        trigger = ingress_result.get("trigger_paragraph")
        http_status = ingress_result.get("http_status") or 200

        if not ingress_result["allowed"]:
            reason = ingress_result.get("reason", "Governance gate blocked execution.")
            hash_ = self._ledger.record_intervention(prompt, trigger, f"HTTP_{http_status}_BLOCKED")
            return SIAResponse(
                content=f"[SIA BLOCKED] {reason}",
                compliant=False,
                action="BLOCKED",
                article_triggered=trigger,
                trace_hash=hash_,
                provider=self._adapter.provider_name,
                confidence=0.0,
                http_status=http_status,
            )

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
                http_status=202,
            )

        # ── 2. MODEL CALL ───────────────────────────────────────────────────
        model_response = self._adapter.generate(
            ingress_result["sanitized_prompt"], **model_kwargs
        )

        # ── 3. EGRESS ───────────────────────────────────────────────────────
        is_compliant, governed_output, watermark, http_headers = self._engine.evaluate_egress(
            model_response.content,
            confidence=model_response.confidence,
            rag_verified=model_response.rag_verified,
            rag_metadata=rag_metadata,
        )

        final_status = 200 if is_compliant else 422   # 422 Unprocessable — output blocked/rewritten
        action = "PASSED" if is_compliant else "REWRITTEN"

        if watermark:
            governed_output += f"\n\n[Transparency]: {watermark}"

        # Add AI-generated header
        http_headers["X-SIA-Provider"] = self._adapter.provider_name
        http_headers["X-SIA-Compliant"] = str(is_compliant).lower()

        # ── 4. TRACEABILITY ─────────────────────────────────────────────────
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
            http_status=final_status,
            http_headers=http_headers,
        )
