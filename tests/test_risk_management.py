import unittest
import time
from pathlib import Path
from sia.core.risk import RuntimeRiskManager, _KILL_SWITCH_FILE
from sia.core.config import EUAIActConfig
from sia.core.engine import RuleEvaluationEngine

class TestRiskManagement(unittest.TestCase):
    def test_input_sanitization(self):
        risk_manager = RuntimeRiskManager()
        
        # Test zero-width space removal
        dirty_prompt = "Hello\u200bWorld"
        self.assertEqual(risk_manager.sanitize_input(dirty_prompt), "HelloWorld")
        
        # Test massive repetition collapse
        noisy_prompt = "Give me access!!!!!!!!!!!"
        self.assertEqual(risk_manager.sanitize_input(noisy_prompt), "Give me access!!!")

    def test_rate_limiting(self):
        risk_manager = RuntimeRiskManager()
        risk_manager.max_requests_per_window = 2
        
        # Request 1
        self.assertTrue(risk_manager.check_rate_limit("user_1"))
        # Request 2
        self.assertTrue(risk_manager.check_rate_limit("user_1"))
        # Request 3 should be blocked
        self.assertFalse(risk_manager.check_rate_limit("user_1"))
        
        # Different user should be allowed
        self.assertTrue(risk_manager.check_rate_limit("user_2"))

    def test_anomaly_detection(self):
        risk_manager = RuntimeRiskManager()
        
        # Normal prompt
        is_anomaly, _ = risk_manager.check_anomaly("This is a normal prompt for testing.")
        self.assertFalse(is_anomaly)
        
        # Extremely long prompt
        is_anomaly, _ = risk_manager.check_anomaly("A" * 10001)
        self.assertTrue(is_anomaly)
        
        # Non-ascii dense prompt
        dense_prompt = "こんにちは" * 20 # 100 chars of non-ascii
        is_anomaly, _ = risk_manager.check_anomaly(dense_prompt)
        self.assertTrue(is_anomaly)

    def test_kill_switch_api(self):
        risk_manager = RuntimeRiskManager()
        self.assertFalse(risk_manager.is_kill_switch_active())
        
        risk_manager.set_kill_switch(True)
        self.assertTrue(risk_manager.is_kill_switch_active())
        
        risk_manager.set_kill_switch(False)
        self.assertFalse(risk_manager.is_kill_switch_active())

    def test_engine_integration_fallback(self):
        from sia.core.config import load_logic_gates
        config = load_logic_gates("configs/eu_ai_act_full.yaml")
        engine = RuleEvaluationEngine(config, "prod")
        
        # Simulate a low confidence egress evaluation
        is_compliant, modified_output, watermark, headers = engine.evaluate_egress(
            output="I am not sure, but here is an answer.",
            confidence=0.5, # Below default 0.85
            rag_verified=False
        )
        
        self.assertFalse(is_compliant)
        self.assertIn("[SIA BLOCK]", modified_output)

if __name__ == "__main__":
    unittest.main()
