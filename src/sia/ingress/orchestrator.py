from typing import Dict, Any
from sia.ingress.classifier import IntentClassifier
from sia.ingress.sanitizer import DataSanitizer
from sia.core.engine import RuleEvaluationEngine

class ContextualIngressOrchestrator:
    def __init__(self, rule_engine: RuleEvaluationEngine):
        self.classifier = IntentClassifier()
        self.sanitizer = DataSanitizer()
        self.rule_engine = rule_engine

    def process_prompt(self, prompt: str) -> Dict[str, Any]:
        intent = self.classifier.classify(prompt)
        
        if intent == "prohibited":
            return {"allowed": False, "reason": "Prohibited intent detected.", "sanitized_prompt": None, "requires_human_review": False}

        contains_pii = self.sanitizer.contains_pii(prompt)
        sanitized_prompt = self.sanitizer.sanitize(prompt)

        # Enforce EU AI Act Ingress Rules
        context = {
            "intent": intent,
            "prompt_text": prompt,
            "contains_pii": contains_pii
        }
        
        eval_result = self.rule_engine.evaluate_ingress(context)
        
        return {
            "allowed": eval_result["allowed"],
            "requires_human_review": eval_result["requires_human_review"],
            "intent": intent,
            "sanitized_prompt": sanitized_prompt,
            "original_prompt": prompt,
            "pii_detected": contains_pii
        }
