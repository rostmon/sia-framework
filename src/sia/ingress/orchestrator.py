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
        # We classify intent first (e.g., hate_speech)
        intent = self.classifier.classify(prompt)
        
        # We also manually flag 'hate_speech' if the word is in the prompt for the PoC
        if "hate_speech" in prompt:
             intent = "hate_speech"
             
        contains_pii = self.sanitizer.contains_pii(prompt)
        sanitized_prompt = self.sanitizer.sanitize(prompt)

        context = {
            "intent": intent,
            "prompt_text": prompt,
            "contains_pii": contains_pii
        }
        
        eval_result = self.rule_engine.evaluate_ingress(context)
        
        if not eval_result["allowed"]:
             return {
                 "allowed": False,
                 "reason": eval_result.get("trigger_reason"),
                 "trigger_paragraph": eval_result.get("trigger_paragraph"),
                 "sanitized_prompt": None,
                 "requires_human_review": False
             }
        
        return {
            "allowed": True,
            "requires_human_review": eval_result["requires_human_review"],
            "trigger_paragraph": eval_result.get("trigger_paragraph"),
            "intent": intent,
            "sanitized_prompt": sanitized_prompt,
            "original_prompt": prompt,
            "pii_detected": contains_pii
        }
