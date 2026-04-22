"""
Example: FastAPI application governed by SIA.
Demonstrates the `SIAMiddleware` for zero-code compliance.
"""
from fastapi import FastAPI, Body
from sia.integrations.fastapi import SIAMiddleware
from sia.adapters.mock_adapter import MockAdapter

app = FastAPI(title="SIA Governed API")

# Add SIA Governance Middleware
app.add_middleware(
    SIAMiddleware,
    config_path="configs/eu_ai_act_full.yaml",
    adapter=MockAdapter(mock_content="This is a compliant medical analysis.")
)

@app.post("/analyze")
async def analyze(prompt: str = Body(..., embed=True)):
    """
    This endpoint is automatically governed by SIAMiddleware.
    Any high-risk intent or PII will be intercepted before reaching this handler.
    """
    return {"result": f"Application processed: {prompt}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8002)
