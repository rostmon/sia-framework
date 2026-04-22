from sia.core.config import load_logic_gates
from sia.core.engine import RuleEvaluationEngine
from sia.ingress.orchestrator import ContextualIngressOrchestrator
from sia.traceability.extractor import ReasoningExtractor
from sia.traceability.ledger import AuditLedger
from sia.egress.validator import DeterministicEgressValidator

def execute_pipeline(prompt: str, mock_llm_output: str, mock_confidence: float):
    config = load_logic_gates("configs/eu_ai_act_full.yaml")
    rule_engine = RuleEvaluationEngine(config, environment="prod")
    ingress = ContextualIngressOrchestrator(rule_engine)
    extractor = ReasoningExtractor()
    ledger = AuditLedger()
    egress = DeterministicEgressValidator()
    
    print(f"\n[Request]: {prompt}")
    ingress_result = ingress.process_prompt(prompt)
    
    if ingress_result.get("requires_human_review"):
        trigger = ingress_result.get("trigger_paragraph", "unknown")
        print(f"[{trigger.upper()} TRIGGERED]: Annex III Category Detected")
        print("Action: HTTP 202 Accepted (Human Veto Required)")
        ledger.record_intervention(prompt, trigger, "HTTP_202_ACCEPTED_HUMAN_VETO")
        return

    is_compliant, verified_output, watermark = rule_engine.evaluate_egress(mock_llm_output, confidence=mock_confidence)
    if watermark:
        verified_output += f"\n\n[Transparency]: {watermark}"

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
    print("=== SIA Framework Proof of Concept (Populating Ledger) ===")
    
    # 1. High-Risk Prompt (Triggers Article 14.4)
    execute_pipeline("Can you run resume scoring for john.doe@example.com?", "Mock output", 0.9)
    
    # 2. Low-Risk Prompt with PII (Triggers Article 10.3 Sanitization)
    execute_pipeline("Summarize the meeting notes for jane.smith@email.com.", "Jane had a good meeting.", 0.9)
    
    # 3. Low-Risk Prompt with Hallucination (Triggers Article 15.3 Block)
    execute_pipeline("Explain quantum computing.", "Quantum computers run on magic dust.", 0.4)

if __name__ == "__main__":
    run_poc()
