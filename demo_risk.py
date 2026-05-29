import asyncio
from sia.adapters.client import SIAClient
from sia.adapters.mock_adapter import MockAdapter

async def main():
    print("Initializing SIA Client with Risk Management...")
    adapter = MockAdapter()
    client = SIAClient(adapter=adapter)

    print("\n--- 1. Triggering Rate Limit ---")
    for i in range(52):  # Limit is 50
        client.chat("Fast request", client_id="test_user_rate_limit")
    print("Rate limit triggered for test_user_rate_limit.")

    print("\n--- 2. Triggering Anomaly / Data Poisoning ---")
    client.chat("こんにちは" * 20)  # Dense non-ascii
    print("Anomaly triggered.")

    print("\n--- 3. Triggering Data Drift ---")
    for i in range(50):
        client.chat("Normal length request about ten words.")
    print("Baseline established. Sending massive input to trigger drift...")
    client.chat("A" * 2000)
    print("Data drift triggered.")

    print("\n--- 4. Low Confidence Fallback ---")
    # To test egress, we need the adapter to return low confidence. 
    # Since HuggingFaceAdapter is a real adapter, it might return valid stuff.
    # We will mock the generate method temporarily just to force a low confidence response.
    original_gen = client._adapter.generate
    def mock_gen(*args, **kwargs):
        from sia.adapters.base import ModelResponse
        return ModelResponse(content="I am not sure what to say.", confidence=0.4, rag_verified=False, provider="mock")
    
    client._adapter.generate = mock_gen
    res = client.chat("Ask something complex")
    print("Fallback response:", res.content)
    client._adapter.generate = original_gen

    print("\nDemo finished. Incidents should now be logged.")

if __name__ == "__main__":
    asyncio.run(main())
