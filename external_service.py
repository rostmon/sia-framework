"""
External AI Service — Simulates an un-governed 'Legacy' AI API.
This service has NO compliance logic.
"""
from fastapi import FastAPI, Request
import uvicorn

app = FastAPI(title="Legacy AI Service")

@app.post("/v1/chat")
async def chat(request: Request):
    data = await request.json()
    prompt = data.get("prompt", "")
    
    # Simulates a 'dumb' AI that just echoes or returns a generic response
    # without any safety or compliance checks.
    if "scoring" in prompt.lower():
        return {"content": "Sure, I can help you with scoring. Here is the data..."}
    
    return {"content": f"Legacy AI says: I received your prompt '{prompt[:20]}...'"}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=9000)
