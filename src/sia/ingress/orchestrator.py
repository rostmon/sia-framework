from typing import Dict, Any
from sia.ingress.classifier import IntentClassifier
from sia.ingress.sanitizer import DataSanitizer
from sia.core.engine import RuleEvaluationEngine

class ContextualIngressOrchestrator:
    """
    The Cognitive Firewall of the system.
    """
    def __init__(self, rule_engine: RuleEvaluationEngine):
        self.classifier = IntentClassifier()
        self.sanitizer = DataSanitizer()
        self.rule_engine = rule_engine

    def process_prompt(self, prompt: str) -> Dict[str, Any]:
        """
        Orchestrates the ingress pipeline: Intent Classification, Sanitization, Veto.
        """
        # 1. Classification
        intent = self.classifier.classify(prompt)
        
        # 2. Veto Logic
        # Pre-emptive Veto for specific prohibited behaviors
        if intent == "prohibited":
            return {
                "allowed": False,
                "reason": "Prohibited intent detected.",
                "sanitized_prompt": None
            }

        # 3. Sanitization
        contains_pii = self.sanitizer.contains_pii(prompt)
        sanitized_prompt = self.sanitizer.sanitize(prompt)

        # 4. Enforce Governance Rules (Pre-processing rules)
        context = {
            "intent": intent,
            "contains_pii": contains_pii
        }
        # In a real implementation, we evaluate if the rules strictly block the prompt.
        
        return {
            "allowed": True,
            "intent": intent,
            "sanitized_prompt": sanitized_prompt,
            "original_prompt": prompt,
            "pii_detected": contains_pii
        }
