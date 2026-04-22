import os
import logging
from typing import Optional
from sia.ingress.governance_prompts import ANNEX_III_CLASSIFICATION_PROMPT, INTENT_DETECTION_PROMPT

logger = logging.getLogger(__name__)

class IntentClassifier:
    """
    Categorizes requests according to EU AI Act Risk Tiers using a hybrid approach:
    1. Heuristics/Keywords (fast, cheap)
    2. LLM-based zero-shot classification (accurate, resilient)
    """

    def __init__(self, use_llm: bool = False, model_adapter = None):
        self.use_llm = use_llm
        self.model_adapter = model_adapter
        self.high_risk_keywords = {
            # Priority 1: Prohibited Practices (BLOCK 451)
            "subliminal_manipulation": ["subliminal"],
            "social_scoring": ["social scoring", "citizen ranking"],
            "exploit_children": ["exploit_children"],
            "exploit_elderly": ["exploit_elderly"],
            "exploit_disability": ["exploit_disability"],
            "real_time_biometrics_public": ["real_time_biometrics_public", "live cctv"],
            
            # Priority 2: Special Categories (BLOCK 403/400)
            "health_data": ["health_data"],
            "hate_speech": ["hate_speech"],
            "deepfake_generation": ["deepfake_generation", "synthetic_voice_impersonation"],

            # Priority 3: High-Risk Annex III (HITL 202)
            "employment": ["resume", "hiring", "interview", "candidate", "job application"],
            "healthcare": ["medical", "diagnosis", "patient", "clinical", "triage"],
            "justice": ["legal verdict", "sentencing", "court", "judge"],
            "biometrics": ["facial recognition", "emotion detection", "fingerprint"],
        }

    def classify(self, prompt: str) -> str:
        # 1. Try Keyword Heuristics first
        keyword_intent = self._classify_by_keywords(prompt)
        if keyword_intent != "none" and not self.use_llm:
            return keyword_intent

        # 2. Use LLM for high-intelligence classification
        if self.use_llm and self.model_adapter:
            return self._classify_by_llm(prompt)

        return keyword_intent if keyword_intent != "none" else "low_risk"

    def _classify_by_keywords(self, prompt: str) -> str:
        prompt_lower = prompt.lower()
        for intent, keywords in self.high_risk_keywords.items():
            if any(kw in prompt_lower for kw in keywords):
                return intent
        return "none"

    def _classify_by_llm(self, prompt: str) -> str:
        """
        Calls the internal model adapter to classify the prompt.
        Note: This uses the model adapter provided at init, allowing for 
        a smaller, faster model (e.g. GPT-3.5) for governance tasks.
        """
        try:
            formatted_prompt = ANNEX_III_CLASSIFICATION_PROMPT.format(prompt=prompt)
            # We use a lower temperature for classification tasks
            response = self.model_adapter.generate(formatted_prompt, temperature=0.0)
            intent = response.content.strip().lower()
            
            valid_intents = [
                "employment", "healthcare", "biometrics", "education", 
                "critical_infra", "law_enforcement", "migration", "justice",
                "social_scoring", "subliminal", "exploit_vulnerable", "prompt_injection"
            ]
            
            if intent in valid_intents:
                return intent
            return "low_risk"
        except Exception as e:
            logger.error(f"LLM Classification failed: {e}")
            return "low_risk"

    def detect_injection(self, prompt: str) -> bool:
        """Specifically checks for adversarial intent."""
        if self.use_llm and self.model_adapter:
            try:
                formatted = INTENT_DETECTION_PROMPT.format(prompt=prompt)
                response = self.model_adapter.generate(formatted, temperature=0.0)
                return response.content.strip().lower() == "prompt_injection"
            except Exception:
                pass
        
        # Fallback to pattern matching
        injection_patterns = ["ignore all previous", "dan mode", "system override"]
        return any(p in prompt.lower() for p in injection_patterns)
