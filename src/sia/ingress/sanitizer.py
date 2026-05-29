import re
import hashlib
import uuid
from typing import Tuple, Dict

class UnifiedDataSanitizer:
    """
    Unified Sensitive Data Schema for SIA.
    Manages Tier 1 (PHI/Special Category) via Pseudonymization/Vaulting
    and Tier 2 (General PII) via Redaction.
    """
    def __init__(self):
        # Tier 2: General PII (Redact or Hash)
        self.email_regex = re.compile(r"[\w\.-]+@[\w\.-]+\.\w+")
        
        # Tier 1: PHI/Special Category (Pseudonymize and Vault)
        # Mocking clinical data detection with SSN/Medical Record Number patterns
        self.ssn_regex = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")
        self.mrn_regex = re.compile(r"\bMRN-\d{6}\b")
        
        # Simulated Vault for Keys
        self._key_vault = {}

    def _pseudonymize(self, match) -> str:
        """Encrypts identifier and returns a token."""
        original_value = match.group(0)
        token = f"TOKEN_{uuid.uuid4().hex[:8]}"
        self._key_vault[token] = original_value # In production: Secure US GovCloud Vault
        return f"[{token}]"

    def sanitize(self, text: str) -> Tuple[str, Dict[str, str]]:
        """
        Processes text according to the Unified Schema.
        Returns the sanitized text and a manifest of detected sensitive data types.
        """
        manifest = {"tier_1_phi": False, "tier_2_pii": False}
        
        # Process Tier 2 (General PII) -> Redaction
        if self.email_regex.search(text):
            manifest["tier_2_pii"] = True
            text = self.email_regex.sub("[REDACTED_EMAIL]", text)

        # Process Tier 1 (PHI/Special) -> Pseudonymization
        if self.ssn_regex.search(text) or self.mrn_regex.search(text):
            manifest["tier_1_phi"] = True
            text = self.ssn_regex.sub(self._pseudonymize, text)
            text = self.mrn_regex.sub(self._pseudonymize, text)

        return text, manifest

    def delete_key(self, token: str) -> bool:
        """
        Simulates the GDPR Purge / Right to Erasure.
        Deleting the key mathematically destroys the PHI.
        """
        if token in self._key_vault:
            del self._key_vault[token]
            return True
        return False

    def contains_sensitive_data(self, text: str) -> bool:
        """Checks if any sensitive data is present."""
        return (self.email_regex.search(text) or 
                self.ssn_regex.search(text) or 
                self.mrn_regex.search(text)) is not None
