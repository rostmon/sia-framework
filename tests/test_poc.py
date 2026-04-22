from sia.core.config import load_logic_gates
from sia.core.engine import RuleEvaluationEngine
from sia.ingress.orchestrator import ContextualIngressOrchestrator
from sia.traceability.extractor import ReasoningExtractor
from sia.traceability.ledger import AuditLedger
from sia.egress.validator import DeterministicEgressValidator

def run_poc():
    print("=== SIA Framework Proof of Concept ===")
    
    # Initialize framework
    config = load_logic_gates("configs/sia_logic_gate.yaml")
    rule_engine = RuleEvaluationEngine(config)
    ingress = ContextualIngressOrchestrator(rule_engine)
    extractor = ReasoningExtractor()
    ledger = AuditLedger()
    egress = DeterministicEgressValidator()
    
    print("\n1. Testing Ingress Orchestrator")
    prompt = "Can you provide medical triage for a patient with SSN 123-45-6789?"
    print(f"Original Prompt: {prompt}")
    
    ingress_result = ingress.process_prompt(prompt)
    if not ingress_result["allowed"]:
        print(f"BLOCK: {ingress_result['reason']}")
        return
        
    print(f"Intent Classified: {ingress_result['intent']}")
    print(f"Sanitized Prompt: {ingress_result['sanitized_prompt']}")
    
    print("\n2. Mock LLM Execution")
    # Simulate LLM Response
    llm_output = "The patient should see a doctor immediately. SIA uses Governance-as-Code to ensure compliance."
    llm_reasoning = "<thought> Need to evaluate triage and mention Governance-as-Code for the rules. </thought>"
    print(f"LLM Output: {llm_output}")
    
    print("\n3. Egress Validator")
    verified_output = egress.validate(llm_output)
    print(f"Final Signed Output:\n{verified_output}")
    
    print("\n4. Traceability Ledger")
    reasoning_path = extractor.extract({"content": llm_reasoning})
    signature_hash = ledger.record_trace(
        prompt=prompt,
        sanitized_prompt=ingress_result["sanitized_prompt"],
        reasoning_path=reasoning_path,
        output=verified_output,
        compliance_score=0.9
    )
    print(f"Audit Trace Recorded with Hash: {signature_hash}")

if __name__ == "__main__":
    run_poc()
