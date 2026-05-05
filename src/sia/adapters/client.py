"""
SIAClient — updated with Async support (achat) and the @governed decorator.
"""
from __future__ import annotations
import functools
import inspect
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional, Callable, TypeVar, Union

from sia.adapters.base import ModelAdapter
from sia.core.config import load_logic_gates
from sia.core.engine import RuleEvaluationEngine
from sia.egress.validator import DeterministicEgressValidator
from sia.ingress.orchestrator import ContextualIngressOrchestrator
from sia.traceability.extractor import ReasoningExtractor
from sia.traceability.ledger import AuditLedger
from sia.core.webhooks import WebhookDispatcher

T = TypeVar("T")

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
    risk_score: float = 0.0                  # Quantified compliance risk (0-100)
    http_headers: Dict[str, str] = field(default_factory=dict)  # e.g. X-SIA-AI-Generated


class SIAClient:
    """Plug-and-play EU AI Act compliance wrapper for any AI/ML model."""

    def __init__(
        self,
        adapter: ModelAdapter,
        config_path: str | Path = "configs/eu_ai_act_full.yaml",
        environment: str = "prod",
        ledger_path: str = "logs/audit_ledger.jsonl",
        governance_adapter: Optional[ModelAdapter] = None,
        webhook_url: Optional[str] = None,
    ):
        self._adapter = adapter
        self._config = load_logic_gates(config_path)
        self._engine = RuleEvaluationEngine(self._config, environment=environment)
        self._ingress = ContextualIngressOrchestrator(self._engine, governance_adapter=governance_adapter)
        self._extractor = ReasoningExtractor()
        self._ledger = AuditLedger(db_path=ledger_path)
        self._egress = DeterministicEgressValidator()
        self._webhooks = WebhookDispatcher(webhook_url=webhook_url)

    def set_kill_switch(self, active: bool):
        """Toggles the global emergency kill-switch."""
        self._engine.risk_manager.set_kill_switch(active)

    def chat(self, prompt: str, rag_metadata: Optional[Dict] = None, **model_kwargs) -> SIAResponse:
        """Synchronous governed chat."""
        # --- 1. INGRESS ---
        ingress_result = self._ingress.process_prompt(prompt)
        if not ingress_result["allowed"]:
            return self._handle_blocked(prompt, ingress_result)
        if ingress_result.get("requires_human_review"):
            return self._handle_veto(prompt, ingress_result)

        # --- 2. MODEL CALL ---
        model_response = self._adapter.generate(
            ingress_result["sanitized_prompt"], **model_kwargs
        )

        # --- 3. EGRESS & TRACE ---
        return self._process_egress(prompt, ingress_result, model_response, rag_metadata)

    async def achat(self, prompt: str, rag_metadata: Optional[Dict] = None, **model_kwargs) -> SIAResponse:
        """Asynchronous governed chat."""
        # --- 1. INGRESS ---
        # Note: Ingress is currently CPU-bound (regex/PII) or sync LLM calls.
        # Future optimization: make ingress fully async if using remote classification.
        ingress_result = self._ingress.process_prompt(prompt)
        if not ingress_result["allowed"]:
            return self._handle_blocked(prompt, ingress_result)
        if ingress_result.get("requires_human_review"):
            return self._handle_veto(prompt, ingress_result)

        # --- 2. MODEL CALL (ASYNC) ---
        model_response = await self._adapter.agenerate(
            ingress_result["sanitized_prompt"], **model_kwargs
        )

        # --- 3. EGRESS & TRACE ---
        return self._process_egress(prompt, ingress_result, model_response, rag_metadata)

    async def astream(self, prompt: str, rag_metadata: Optional[Dict] = None, **model_kwargs):
        """Asynchronous streaming governed chat."""
        # --- 1. INGRESS ---
        ingress_result = self._ingress.process_prompt(prompt)
        if not ingress_result["allowed"]:
            blocked_response = self._handle_blocked(prompt, ingress_result)
            yield blocked_response.content
            return
        if ingress_result.get("requires_human_review"):
            veto_response = self._handle_veto(prompt, ingress_result)
            yield veto_response.content
            return

        # --- 2. MODEL CALL (STREAM) ---
        accumulated_content = ""
        
        async for chunk in self._adapter.astream(ingress_result["sanitized_prompt"], **model_kwargs):
            accumulated_content += chunk
            
            # Mid-stream egress scan
            is_compliant, _, watermark, _ = self._engine.evaluate_egress(
                accumulated_content, confidence=0.9, rag_verified=True, rag_metadata=rag_metadata
            )
            
            if not is_compliant:
                intercept_msg = "\n\n[SIA INTERCEPTED] Generated stream violated compliance rules and was halted."
                yield intercept_msg
                self._ledger.record_trace(
                    prompt=prompt,
                    sanitized_prompt=ingress_result["sanitized_prompt"],
                    reasoning_path={},
                    output=accumulated_content + intercept_msg,
                    compliance_score=0.0
                )
                return
                
            yield chunk

        # --- 3. END OF STREAM (Transparency & Trace) ---
        is_compliant, _, watermark, _ = self._engine.evaluate_egress(
            accumulated_content, confidence=0.9, rag_verified=True, rag_metadata=rag_metadata
        )
        
        if watermark:
             yield f"\n\n[Transparency]: {watermark}"
             
        self._ledger.record_trace(
            prompt=prompt,
            sanitized_prompt=ingress_result["sanitized_prompt"],
            reasoning_path={},
            output=accumulated_content + (f"\n\n[Transparency]: {watermark}" if watermark else ""),
            compliance_score=0.9
        )


    def _handle_blocked(self, prompt: str, ingress_result: Dict) -> SIAResponse:
        trigger = ingress_result.get("trigger_paragraph")
        http_status = ingress_result.get("http_status") or 403
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
            risk_score=ingress_result.get("risk_score", 100.0)
        )

    def _handle_veto(self, prompt: str, ingress_result: Dict) -> SIAResponse:
        trigger = ingress_result.get("trigger_paragraph")
        hash_ = self._ledger.record_intervention(prompt, trigger, "HTTP_202_ACCEPTED_HUMAN_VETO")
        
        # Dispatch HITL notification
        self._webhooks.notify_intervention_sync(
            prompt=prompt,
            article=trigger or "article_14_4",
            trace_hash=hash_,
            context={"intent": ingress_result.get("intent")}
        )

        return SIAResponse(
            content="[SIA HUMAN VETO] This request requires human review before processing.",
            compliant=False,
            action="HUMAN_VETO",
            article_triggered=trigger,
            trace_hash=hash_,
            provider=self._adapter.provider_name,
            confidence=0.0,
            http_status=202,
            risk_score=ingress_result.get("risk_score", 100.0)
        )

    def _process_egress(self, prompt: str, ingress_result: Dict, model_response: Any, rag_metadata: Optional[Dict]) -> SIAResponse:
        is_compliant, governed_output, watermark, http_headers = self._engine.evaluate_egress(
            model_response.content,
            confidence=model_response.confidence,
            rag_verified=model_response.rag_verified,
            rag_metadata=rag_metadata,
        )

        final_status = 200 if is_compliant else 422
        action = "PASSED" if is_compliant else "REWRITTEN"

        if watermark:
            governed_output += f"\n\n[Transparency]: {watermark}"

        http_headers["X-SIA-Provider"] = self._adapter.provider_name
        http_headers["X-SIA-Compliant"] = str(is_compliant).lower()

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
            risk_score=ingress_result.get("risk_score", 0.0)
        )


def governed(client: SIAClient, rag_metadata: Optional[Dict] = None, rag_verified: bool = True):
    """
    Decorator to wrap any function that takes a prompt and returns a string
    with EU AI Act governance.

    Args:
        client: SIAClient instance.
        rag_metadata: Optional metadata for RAG grounding verification.
        rag_verified: Whether the output should be considered grounded. Default True.
    """
    def decorator(func: Callable[..., Any]):
        if inspect.isasyncgenfunction(func):
            @functools.wraps(func)
            async def async_gen_wrapper(prompt: str, *args, **kwargs):
                ingress_result = client._ingress.process_prompt(prompt)
                if not ingress_result["allowed"]:
                    yield client._handle_blocked(prompt, ingress_result).content
                    return
                if ingress_result.get("requires_human_review"):
                    yield client._handle_veto(prompt, ingress_result).content
                    return
                
                accumulated_content = ""
                async for chunk in func(ingress_result["sanitized_prompt"], *args, **kwargs):
                    accumulated_content += chunk
                    is_compliant, _, _, _ = client._engine.evaluate_egress(
                        accumulated_content, confidence=0.9, rag_verified=rag_verified, rag_metadata=rag_metadata
                    )
                    if not is_compliant:
                        intercept_msg = "\n\n[SIA INTERCEPTED] Generated stream violated compliance rules and was halted."
                        yield intercept_msg
                        client._ledger.record_trace(
                            prompt=prompt,
                            sanitized_prompt=ingress_result["sanitized_prompt"],
                            reasoning_path={},
                            output=accumulated_content + intercept_msg,
                            compliance_score=0.0
                        )
                        return
                    yield chunk

                is_compliant, _, watermark, _ = client._engine.evaluate_egress(
                    accumulated_content, confidence=0.9, rag_verified=rag_verified, rag_metadata=rag_metadata
                )
                if watermark:
                    yield f"\n\n[Transparency]: {watermark}"
                    
                client._ledger.record_trace(
                    prompt=prompt,
                    sanitized_prompt=ingress_result["sanitized_prompt"],
                    reasoning_path={},
                    output=accumulated_content + (f"\n\n[Transparency]: {watermark}" if watermark else ""),
                    compliance_score=0.9
                )
            return async_gen_wrapper
        elif inspect.iscoroutinefunction(func):
            @functools.wraps(func)
            async def async_wrapper(prompt: str, *args, **kwargs):
                # 1. Ingress
                ingress_result = client._ingress.process_prompt(prompt)
                if not ingress_result["allowed"]:
                    return client._handle_blocked(prompt, ingress_result).content
                if ingress_result.get("requires_human_review"):
                    return client._handle_veto(prompt, ingress_result).content
                
                # 2. Call original function (sanitized prompt)
                result = await func(ingress_result["sanitized_prompt"], *args, **kwargs)
                
                # 3. Egress (simulated response for processing)
                from sia.adapters.base import ModelResponse
                fake_response = ModelResponse(content=result, confidence=0.9, 
                                            rag_verified=rag_verified, provider="wrapped_func")
                governed_res = client._process_egress(prompt, ingress_result, fake_response, rag_metadata)
                return governed_res.content
            return async_wrapper
        else:
            @functools.wraps(func)
            def sync_wrapper(prompt: str, *args, **kwargs):
                ingress_result = client._ingress.process_prompt(prompt)
                if not ingress_result["allowed"]:
                    return client._handle_blocked(prompt, ingress_result).content
                if ingress_result.get("requires_human_review"):
                    return client._handle_veto(prompt, ingress_result).content
                
                result = func(ingress_result["sanitized_prompt"], *args, **kwargs)
                
                from sia.adapters.base import ModelResponse
                fake_response = ModelResponse(content=result, confidence=0.9, 
                                            rag_verified=rag_verified, provider="wrapped_func")
                governed_res = client._process_egress(prompt, ingress_result, fake_response, rag_metadata)
                return governed_res.content
            return sync_wrapper
    return decorator
