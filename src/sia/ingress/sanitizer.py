import re

class DataSanitizer:
    """
    Automated PII stripping before the prompt reaches the LLM.
    """
    def __init__(self):
        # Stub implementation. 
        # In production, use Microsoft Presidio for robust PII detection.
        self.email_regex = re.compile(r"[\w\.-]+@[\w\.-]+\.\w+")
        self.ssn_regex = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")

    def sanitize(self, text: str) -> str:
        """
        Replaces PII with redacted placeholders.
        """
        text = self.email_regex.sub("[REDACTED_EMAIL]", text)
        text = self.ssn_regex.sub("[REDACTED_SSN]", text)
        return text

    def contains_pii(self, text: str) -> bool:
        """
        Checks if text contains PII without redacting.
        """
        if self.email_regex.search(text) or self.ssn_regex.search(text):
            return True
        return False
