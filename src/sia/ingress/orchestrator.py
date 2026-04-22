from typing import Dict, Any, Optional
from sia.ingress.classifier import IntentClassifier
from sia.ingress.sanitizer import DataSanitizer
from sia.core.engine import RuleEvaluationEngine


class ContextualIngressOrchestrator:
    """
    Ingress layer: classifies intent, sanitizes PII, then runs all
    EU AI Act governance gates via the RuleEvaluationEngine.
    """

    # Explicit intent mappings for PoC deterministic testing
    _INTENT_MAP = {
        # Article 5 prohibited
        "social scoring":                  "social_scoring",
        "social_scoring":                  "social_scoring",
        "citizen_ranking":                 "citizen_ranking",
        "subliminal":                      "subliminal_manipulation",
        "exploit_elderly":                 "exploit_elderly",
        "exploit_disability":              "exploit_disability",
        "exploit_children":                "exploit_children",
        "real_time_biometrics_public":     "real_time_biometrics_public",
        "live cctv":                       "live_cctv_face_match",
        # Article 10.2f bias
        "hate_speech":                     "hate_speech",
        "discriminatory_inference":        "discriminatory_inference",
        "racial_profiling":                "racial_profiling",
        # Article 10.5 special categories
        "health_data":                     "health_data",
        "political_opinions":              "political_opinions",
        # Article 50.2 deepfakes
        "deepfake_generation":             "deepfake_generation",
        "synthetic_voice_impersonation":   "synthetic_voice_impersonation",
    }

    def __init__(self, rule_engine: RuleEvaluationEngine):
        self.classifier = IntentClassifier()
        self.sanitizer = DataSanitizer()
        self.rule_engine = rule_engine

    def process_prompt(self, prompt: str) -> Dict[str, Any]:
        # Classify intent
        intent = self.classifier.classify(prompt)

        # Override with explicit keyword matching for PoC determinism
        prompt_lower = prompt.lower()
        for keyword, mapped_intent in self._INTENT_MAP.items():
            if keyword in prompt_lower:
                intent = mapped_intent
                break

        # Prompt injection patterns
        injection_patterns = ["IGNORE ALL PREVIOUS INSTRUCTIONS", "DAN MODE", "SYSTEM_OVERRIDE"]
        if any(p.lower() in prompt.lower() for p in injection_patterns):
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
