from typing import Dict, Any, Optional
import hashlib
from sia.ingress.classifier import IntentClassifier
from sia.ingress.sanitizer import DataSanitizer
from sia.core.engine import RuleEvaluationEngine
from sia.core.cache import GovernanceCache


class ContextualIngressOrchestrator:
    """
    Ingress layer: classifies intent, sanitizes PII, then runs all
    EU AI Act governance gates via the RuleEvaluationEngine.
    """

    def __init__(self, rule_engine: RuleEvaluationEngine, governance_adapter=None, cache_size: int = 1000):
        self.rule_engine = rule_engine
        self.classifier = IntentClassifier(
            use_llm=governance_adapter is not None,
            model_adapter=governance_adapter
        )
        self.sanitizer = DataSanitizer()
        self.cache = GovernanceCache(max_size=cache_size)

    def _get_prompt_hash(self, prompt: str) -> str:
        return hashlib.sha256(prompt.encode("utf-8")).hexdigest()

    def process_prompt(self, prompt: str) -> Dict[str, Any]:
        # --- 0. CACHE LOOKUP ---
        prompt_hash = self._get_prompt_hash(prompt)
        cached_result = self.cache.get(prompt_hash)
        if cached_result:
            return cached_result

        # 1. Advanced Intent Classification (Hybrid)
        intent = self.classifier.classify(prompt)

        # 2. Adversarial Intent Detection (Injection/Jailbreak)
        if self.classifier.detect_injection(prompt):
            intent = "prompt_injection"

        contains_pii = self.sanitizer.contains_pii(prompt)
        sanitized_prompt = self.sanitizer.sanitize(prompt)

        context = {
            "intent": intent,
            "prompt_text": prompt,
            "contains_pii": contains_pii,
        }

        eval_result = self.rule_engine.evaluate_ingress(context)

        if not eval_result["allowed"]:
            return {
                "allowed": False,
                "reason": eval_result.get("trigger_reason"),
                "trigger_paragraph": eval_result.get("trigger_paragraph"),
                "http_status": eval_result.get("http_status", 403),
                "sanitized_prompt": None,
                "requires_human_review": False,
            }

        res = {
            "allowed": True,
            "requires_human_review": eval_result["requires_human_review"],
            "trigger_paragraph": eval_result.get("trigger_paragraph"),
            "http_status": eval_result.get("http_status"),
            "intent": intent,
            "sanitized_prompt": sanitized_prompt,
            "original_prompt": prompt,
            "pii_detected": contains_pii,
        }
        
        # Cache the result
        self.cache.set(self._get_prompt_hash(prompt), res)
        return res
