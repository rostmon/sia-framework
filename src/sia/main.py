from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
import time

from sia.core.config import load_logic_gates
from sia.core.engine import RuleEvaluationEngine
from sia.ingress.orchestrator import ContextualIngressOrchestrator
from sia.traceability.extractor import ReasoningExtractor
from sia.traceability.ledger import AuditLedger
from sia.egress.validator import DeterministicEgressValidator

# Setup core components
config = load_logic_gates("configs/sia_logic_gate.yaml")
rule_engine = RuleEvaluationEngine(config)
ingress = ContextualIngressOrchestrator(rule_engine)
extractor = ReasoningExtractor()
ledger = AuditLedger()
egress = DeterministicEgressValidator()

app = FastAPI(
    title="Sovereign Systemic Integrity Architecture (SIA)",
    description="Governance-as-Code Middleware API"
)

class ChatRequest(BaseModel):
    prompt: str
    # other standard OpenAI-like params can go here

class ChatResponse(BaseModel):
    output: str
    signature_hash: str

@app.post("/v1/chat/completions", response_model=ChatResponse)
async def chat_completion(request: ChatRequest):
    """
    SIA Proxy / Middleware interface.
    Intercepts the request, processes it through the Sovereign Stack,
    and returns a verified output.
    """
    # 1. Ingress - Contextual Firewall
    ingress_result = ingress.process_prompt(request.prompt)
    if not ingress_result["allowed"]:
        raise HTTPException(status_code=403, detail=ingress_result["reason"])

    sanitized_prompt = ingress_result["sanitized_prompt"]

    # 2. Primary Engine (Mock LLM Call)
    # In production, this proxies the call to OpenAI, Anthropic, or local LLM.
    # We use a simulated LLM execution for PoC.
    llm_output_text = "Here is the response. SIA uses Governance-as-Code."
    llm_reasoning = "<thought> I should mention Governance-as-Code. </thought>"

    # 3. Egress - Deterministic Validator
    verified_output = egress.validate(llm_output_text)

    # 4. Traceability - Forensic Ledger
    reasoning_path = extractor.extract({"content": llm_reasoning})
    # We grab the compliance score heuristically from the signature logic in PoC
    compliance_score = 0.9 if "COMPLIANT" in verified_output else 0.0
    
    signature_hash = ledger.record_trace(
        prompt=request.prompt,
        sanitized_prompt=sanitized_prompt,
        reasoning_path=reasoning_path,
        output=verified_output,
        compliance_score=compliance_score
    )

    return ChatResponse(output=verified_output, signature_hash=signature_hash)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
