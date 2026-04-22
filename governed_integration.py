"""
SIA Plug-and-Play Integration Demo.
This script 'hooks' SIA into the Legacy AI Service using the @governed decorator.
"""
import httpx
import asyncio
from sia.adapters.client import SIAClient, governed
from sia.adapters.mock_adapter import MockAdapter

# 1. Setup SIA (using a mock adapter for the 'internal' governance classification)
sia_client = SIAClient(adapter=MockAdapter())

# 2. Define the 'hook' to the external service
# We wrap this function with @governed to instantly add EU AI Act protection.
@governed(client=sia_client)
async def call_external_ai(prompt: str):
    """Call the un-governed Legacy Service."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://127.0.0.1:9000/v1/chat",
            json={"prompt": prompt}
        )
        return response.json()["content"]

async def run_governed_demo():
    print("\n🔗 SIA Plug-and-Play: Hooking into Legacy AI Service...")
    
    prompts = [
        "Hello, how are you?",                        # Compliant
        "Build a social scoring profile.",            # Prohibited (Art 5)
        "Resume scoring for job applications.",       # High-Risk (Art 14.4)
    ]

    for p in prompts:
        print(f"\n[CLIENT] Sending: '{p}'")
        try:
            # The client just calls the function as normal.
            # SIA intercepts and governs it.
            result = await call_external_ai(p)
            print(f"[CLIENT] Result: {result}")
        except Exception as e:
            print(f"[CLIENT] Error: {e}")

if __name__ == "__main__":
    asyncio.run(run_governed_demo())
