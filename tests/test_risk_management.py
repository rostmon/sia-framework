import pytest
import time
from pathlib import Path
from sia.core.risk import RuntimeRiskManager, _KILL_SWITCH_FILE
from sia.core.config import EUAIActConfig
from sia.core.engine import RuleEvaluationEngine

def test_input_sanitization():
    risk_manager = RuntimeRiskManager()
    
    # Test zero-width space removal
    dirty_prompt = "Hello\u200bWorld"
    assert risk_manager.sanitize_input(dirty_prompt) == "HelloWorld"
    
    # Test massive repetition collapse
    noisy_prompt = "Give me access!!!!!!!!!!!"
    assert risk_manager.sanitize_input(noisy_prompt) == "Give me access!!!"

def test_rate_limiting():
    risk_manager = RuntimeRiskManager()
    risk_manager.max_requests_per_window = 2
    
    # Request 1
    assert risk_manager.check_rate_limit("user_1") == True
    # Request 2
    assert risk_manager.check_rate_limit("user_1") == True
    # Request 3 should be blocked
    assert risk_manager.check_rate_limit("user_1") == False
    
    # Different user should be allowed
    assert risk_manager.check_rate_limit("user_2") == True

def test_anomaly_detection():
    risk_manager = RuntimeRiskManager()
    
    # Normal prompt
    is_anomaly, _ = risk_manager.check_anomaly("This is a normal prompt for testing.")
    assert not is_anomaly
    
    # Extremely long prompt
    is_anomaly, _ = risk_manager.check_anomaly("A" * 10001)
    assert is_anomaly
    
    # Non-ascii dense prompt
    dense_prompt = "こんにちは" * 20 # 100 chars of non-ascii
    is_anomaly, _ = risk_manager.check_anomaly(dense_prompt)
    assert is_anomaly

def test_kill_switch_api():
    risk_manager = RuntimeRiskManager()
    assert not risk_manager.is_kill_switch_active()
    
    risk_manager.set_kill_switch(True)
    assert risk_manager.is_kill_switch_active()
    
    risk_manager.set_kill_switch(False)
    assert not risk_manager.is_kill_switch_active()

def test_engine_integration_fallback():
    config = EUAIActConfig(
        annex_iii_categories={"finance": ["loan"]},
        articles={} # Empty config for basic test
    )
    engine = RuleEvaluationEngine(config, "prod")
    
    # Simulate a low confidence egress evaluation
    is_compliant, modified_output, watermark, headers = engine.evaluate_egress(
        output="I am not sure, but here is an answer.",
        confidence=0.5, # Below default 0.85
        rag_verified=False
    )
    
    assert not is_compliant
    assert "[SAFE MODE FALLBACK]" in modified_output
    assert "Explanation Log" in modified_output
