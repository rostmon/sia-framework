from typing import Dict, Any, Optional
from sia.ingress.classifier import IntentClassifier
from sia.ingress.sanitizer import DataSanitizer
from sia.core.engine import RuleEvaluationEngine


class ContextualIngressOrchestrator:
    """
    Ingress layer: classifies intent, sanitizes PII, then runs all
    EU AI Act governance gates via the RuleEvaluationEngine.
    """

    def __init__(self, rule_engine: RuleEvaluationEngine, governance_adapter=None):
        self.rule_engine = rule_engine
        # Initialize classifier with optional LLM adapter for high-intelligence mode
        self.classifier = IntentClassifier(
            use_llm=governance_adapter is not None,
            model_adapter=governance_adapter
        )
        self.sanitizer = DataSanitizer()

    def process_prompt(self, prompt: str) -> Dict[str, Any]:
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

        return {
            "allowed": True,
            "requires_human_review": eval_result["requires_human_review"],
            "trigger_paragraph": eval_result.get("trigger_paragraph"),
            "http_status": eval_result.get("http_status"),
            "intent": intent,
            "sanitized_prompt": sanitized_prompt,
            "original_prompt": prompt,
            "pii_detected": contains_pii,
        }
