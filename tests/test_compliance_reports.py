import unittest
import shutil
import tempfile
from pathlib import Path
from sia.cli.generate_risk_report import load_hazards, load_mitigations, build_index, build_cross_ref, main

class TestComplianceReports(unittest.TestCase):
    def test_load_hazards(self):
        hazards = load_hazards()
        self.assertIn("HZ-01", hazards)
        self.assertIn("HZ-22", hazards)
        self.assertIn("HZ-23", hazards)
        self.assertIn("HZ-24", hazards)
        self.assertIn("HZ-25", hazards)
        self.assertIn("HZ-26", hazards)

        # Verify AAMI citations
        self.assertIn("aami_tir34971", hazards["HZ-24"]["regulatory_citations"])
        self.assertIn("aami_tir34971", hazards["HZ-25"]["regulatory_citations"])
        self.assertIn("aami_tir34971", hazards["HZ-26"]["regulatory_citations"])

    def test_build_index(self):
        hazards = load_hazards()
        mitigations = load_mitigations()
        index_content = build_index(hazards, mitigations, "2026-06-03 12:00 UTC")
        self.assertIn("AAMI TIR34971", index_content)
        self.assertIn("ISO/IEC 42001", index_content)

    def test_build_overview(self):
        from sia.cli.generate_risk_report import build_overview
        hazards = load_hazards()
        mitigations = load_mitigations()
        overview_content = build_overview(hazards, mitigations, "2026-06-03 12:00 UTC")
        self.assertIn("SIA Mitigation Logic & Controls Registry", overview_content)
        self.assertIn("VALIDATE_PROFILE_MATCH", overview_content)
        self.assertIn("BLOCK_OOD_PAYLOAD", overview_content)
        self.assertIn("APPEND_CONFIDENCE_TELEMETRY", overview_content)

    def test_build_cross_ref(self):
        hazards = load_hazards()
        cross_ref_content = build_cross_ref(hazards, [])
        self.assertIn("EU AI Act", cross_ref_content)
        self.assertIn("GDPR", cross_ref_content)

    def test_mitigation_consistency(self):
        hazards = load_hazards()
        mitigations = load_mitigations()
        
        # Verify mitigation registry is loaded and has entries
        self.assertTrue(len(mitigations) > 0)
        self.assertIn("VALIDATE_PROFILE_MATCH", mitigations)
        self.assertIn("BLOCK_OOD_PAYLOAD", mitigations)
        self.assertIn("APPEND_CONFIDENCE_TELEMETRY", mitigations)
        
        # Every hazard's sia_mitigation_logic must be defined in the mitigation registry
        for hz_id, h in hazards.items():
            logic = h.get("sia_mitigation_logic")
            self.assertIn(logic, mitigations, f"Hazard {hz_id} uses mitigation logic {logic} which is missing from mitigation_registry.yaml")

if __name__ == "__main__":
    unittest.main()
