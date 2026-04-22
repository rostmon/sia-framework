from fastapi import FastAPI, HTTPException, Request, Response
from pydantic import BaseModel
from sia.core.config import load_logic_gates
from sia.core.engine import RuleEvaluationEngine
from sia.ingress.orchestrator import ContextualIngressOrchestrator
from sia.traceability.extractor import ReasoningExtractor
from sia.traceability.ledger import AuditLedger
from sia.egress.validator import DeterministicEgressValidator

config = load_logic_gates("configs/eu_ai_act_full.yaml")
rule_engine = RuleEvaluationEngine(config, environment="prod")
ingress = ContextualIngressOrchestrator(rule_engine)
extractor = ReasoningExtractor()
ledger = AuditLedger()
egress = DeterministicEgressValidator()

app = FastAPI(title="Sovereign Systemic Integrity Architecture (SIA)")

class ChatRequest(BaseModel):
    prompt: str

class ChatResponse(BaseModel):
    output: str
    signature_hash: Optional[str] = None
    status: str

@app.post("/v1/chat/completions")
async def chat_completion(request: ChatRequest, response: Response):
    # 1. Ingress - Contextual Firewall
    ingress_result = ingress.process_prompt(request.prompt)
    if not ingress_result["allowed"]:
        raise HTTPException(status_code=403, detail=ingress_result["reason"])

    # Article 14: Human-in-the-loop (HITL) Gate
    if ingress_result.get("requires_human_review"):
        response.status_code = 202
        return {
            "status": "HTTP 202 Accepted - Human Review Required",
            "message": "This request falls under Annex III High-Risk categorization and requires a mandatory human signature before proceeding.",
            "review_url": "https://sia.internal/review/queue/12345"
        }

    sanitized_prompt = ingress_result["sanitized_prompt"]

    # 2. Mock LLM Call
    llm_output_text = "Here is the response. SIA uses Governance-as-Code."
    llm_reasoning = "<thought> I should mention Governance-as-Code. </thought>"

    # 3. Egress - Deterministic Validator
    # We pass the engine to validate Article 13 & 15
    is_compliant, verified_output, watermark = rule_engine.evaluate_egress(llm_output_text, confidence=0.9)
    
    if watermark:
        verified_output += f"\n\n[Transparency]: {watermark}"

    # 4. Traceability - Forensic Ledger
    reasoning_path = extractor.extract({"content": llm_reasoning})
    compliance_score = 0.9 if is_compliant else 0.0
    
    signature_hash = ledger.record_trace(
        prompt=request.prompt,
        sanitized_prompt=sanitized_prompt,
        reasoning_path=reasoning_path,
        output=verified_output,
        compliance_score=compliance_score
    )

    return {"output": verified_output, "signature_hash": signature_hash, "status": "COMPLETED"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
