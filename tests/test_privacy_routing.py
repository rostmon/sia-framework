import unittest
from sia.ingress.sanitizer import UnifiedDataSanitizer
from sia.core.engine import RegulatoryRouter

class TestPrivacyRouting(unittest.TestCase):
    def setUp(self):
        self.sanitizer = UnifiedDataSanitizer()
        self.router = RegulatoryRouter()

    def test_tier2_redaction(self):
        text = "Contact me at user@example.com."
        sanitized, manifest = self.sanitizer.sanitize(text)
        self.assertTrue(manifest["tier_2_pii"])
        self.assertFalse(manifest["tier_1_phi"])
        self.assertIn("[REDACTED_EMAIL]", sanitized)
        self.assertNotIn("user@example.com", sanitized)

    def test_tier1_pseudonymization(self):
        text = "Patient SSN is 123-45-6789 and MRN-123456."
        sanitized, manifest = self.sanitizer.sanitize(text)
        self.assertTrue(manifest["tier_1_phi"])
        self.assertIn("[TOKEN_", sanitized)
        self.assertNotIn("123-45-6789", sanitized)
        
        # Test Vault Logic
        tokens = [k for k, v in self.sanitizer._key_vault.items() if v == "123-45-6789"]
        self.assertEqual(len(tokens), 1)
        
        # Test Purge
        self.sanitizer.delete_key(tokens[0])
        self.assertNotIn(tokens[0], self.sanitizer._key_vault)

    def test_regulatory_router_eu(self):
        context = {"user_location": "EU"}
        config = self.router.resolve_policies("HYBRID_CLINICAL_TRIAL", context)
        self.assertIn("STRICT_GDPR_ENFORCEMENT", config["policies"])
        self.assertEqual(config["retention_days"], 30)

    def test_regulatory_router_us(self):
        context = {"user_location": "US"}
        config = self.router.resolve_policies("HYBRID_CLINICAL_TRIAL", context)
        self.assertIn("HIPAA_RETENTION_LOCK", config["policies"])
        self.assertEqual(config["retention_days"], 2190)

if __name__ == "__main__":
    unittest.main()
