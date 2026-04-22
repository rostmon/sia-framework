from sia.core.config import load_logic_gates
from sia.core.engine import RuleEvaluationEngine
from sia.ingress.orchestrator import ContextualIngressOrchestrator
from sia.traceability.extractor import ReasoningExtractor
from sia.traceability.ledger import AuditLedger
from sia.egress.validator import DeterministicEgressValidator

def run_poc():
    print("=== SIA Framework Proof of Concept (EU AI Act - Paragraph Level) ===")
    
    config = load_logic_gates("configs/eu_ai_act_full.yaml")
    rule_engine = RuleEvaluationEngine(config, environment="prod")
    ingress = ContextualIngressOrchestrator(rule_engine)
    extractor = ReasoningExtractor()
    ledger = AuditLedger()
    egress = DeterministicEgressValidator()
    
    prompt = "Can you run resume scoring for this candidate? Email is john.doe@example.com."
    print(f"\nOriginal Prompt: {prompt}")
    
    ingress_result = ingress.process_prompt(prompt)
    
    if ingress_result.get("requires_human_review"):
        trigger = ingress_result.get("trigger_paragraph", "unknown")
        print(f"\n[{trigger.upper()} TRIGGERED]: High-Risk Category Detected (Annex III)")
        print("Status: HTTP 202 Accepted")
        print("Action: Request paused. Awaiting mandatory human signature.")
        return

    print("\nExecuting Pipeline (Standard Flow)...")

if __name__ == "__main__":
    run_poc()
