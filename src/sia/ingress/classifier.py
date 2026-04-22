class IntentClassifier:
    """
    Categorizes requests according to EU AI Act Risk Tiers.
    """
    def __init__(self):
        # In a real implementation, this would use an ML model or heuristics
        # to classify the prompt intent based on High-Risk tasks.
        self.high_risk_keywords = ["medical triage", "resume scoring", "credit check", "clinical"]

    def classify(self, prompt: str) -> str:
        prompt_lower = prompt.lower()
        if any(kw in prompt_lower for kw in self.high_risk_keywords):
            return "high_risk"
        return "low_risk"
