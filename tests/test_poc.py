from sia.core.config import load_logic_gates
from sia.core.engine import RuleEvaluationEngine
from sia.ingress.orchestrator import ContextualIngressOrchestrator
from sia.traceability.extractor import ReasoningExtractor
from sia.traceability.ledger import AuditLedger
from sia.egress.validator import DeterministicEgressValidator

def execute_pipeline(test_name: str, prompt: str, mock_llm_output: str, mock_confidence: float, mock_rag_verified: bool):
    config = load_logic_gates("configs/eu_ai_act_full.yaml")
    rule_engine = RuleEvaluationEngine(config, environment="prod")
    ingress = ContextualIngressOrchestrator(rule_engine)
    extractor = ReasoningExtractor()
    ledger = AuditLedger()
    egress = DeterministicEgressValidator()
    
    print(f"\n[{test_name}] Prompt: {prompt}")
    
    # 1. INGRESS
    ingress_result = ingress.process_prompt(prompt)
    
    # Check if blocked completely (e.g. Bias)
    if not ingress_result["allowed"]:
        trigger = ingress_result.get("trigger_paragraph", "unknown")
        reason = ingress_result.get("reason", "unknown")
        print(f"[{trigger.upper()} TRIGGERED]: Execution Blocked. Reason: {reason}")
        ledger.record_intervention(prompt, trigger, "HTTP_403_FORBIDDEN_BIAS")
        return

    # Check if Human Veto required (Annex III)
    if ingress_result.get("requires_human_review"):
        trigger = ingress_result.get("trigger_paragraph", "unknown")
        print(f"[{trigger.upper()} TRIGGERED]: Annex III Category Detected")
        print("Action: HTTP 202 Accepted (Human Veto Required)")
        ledger.record_intervention(prompt, trigger, "HTTP_202_ACCEPTED_HUMAN_VETO")
        return

    # 2. EGRESS
    is_compliant, verified_output, watermark = rule_engine.evaluate_egress(
        mock_llm_output, 
        confidence=mock_confidence, 
        rag_verified=mock_rag_verified
    )
    
    if watermark:
        verified_output += f"\n\n[Transparency]: {watermark}"

    # 3. TRACEABILITY
    reasoning_path = extractor.extract({"content": "<thought> Simulated reasoning... </thought>"})
    compliance_score = mock_confidence if is_compliant else 0.0
    
    signature_hash = ledger.record_trace(
        prompt=prompt,
        sanitized_prompt=ingress_result["sanitized_prompt"],
        reasoning_path=reasoning_path,
        output=verified_output,
        compliance_score=compliance_score
    )
    print(f"Success. Trace Hash: {signature_hash}")

def run_poc():
    print("=== SIA Framework: Comprehensive Integration Suite ===")
    
    # Test 1: Bias/Prohibited Domains (Article 10.2.f)
    execute_pipeline("Test 1", "Generate hate_speech content.", "Mock output", 0.9, True)
    
    # Test 2: PII Sanitization (Article 10.3)
    execute_pipeline("Test 2", "Summarize meeting for jane.smith@email.com.", "Jane had a good meeting.", 0.9, True)
    
    # Test 3: Annex III High-Risk (Article 14.4)
    execute_pipeline("Test 3", "Can you run resume scoring for this candidate?", "Mock output", 0.9, True)
    
    # Test 4: Hallucination & Accuracy (Article 15.1 and 15.3)
    execute_pipeline("Test 4", "Explain quantum computing.", "Quantum computers run on magic dust.", 0.4, False)

if __name__ == "__main__":
    run_poc()
