"""
Tests for Phase 3.1: Streaming Governance.
Verifies that SIA can govern AsyncGenerator streams.
"""
import unittest
import asyncio
from sia.adapters.client import SIAClient, governed
from sia.adapters.mock_adapter import MockAdapter

class TestStreamingGovernance(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.sia_client = SIAClient(adapter=MockAdapter())

    async def test_streaming_pass_with_watermark(self):
        """Test that a compliant stream is allowed and transparently watermarked."""
        
        @governed(client=self.sia_client)
        async def compliant_stream(prompt):
            for word in ["This ", "is ", "a ", "compliant ", "stream."]:
                yield word
                await asyncio.sleep(0.01)
                
        chunks = []
        async for chunk in compliant_stream("Hello, stream"):
            chunks.append(chunk)
            
        full_text = "".join(chunks)
        self.assertIn("compliant stream", full_text)
        self.assertIn("[Transparency]", full_text)
        
    async def test_streaming_intercepted_midstream(self):
        """Test that a stream violating rules is intercepted mid-stream."""
        
        @governed(client=self.sia_client, rag_metadata={"source_domain": "external_web"}, rag_verified=True)
        async def violating_stream(prompt):
            # 'external_web' is not allowlisted in copyright check (only internal_wiki is allowed)
            for word in ["This ", "is ", "copyrighted ", "material ", "stream."]:
                yield word
                await asyncio.sleep(0.01)
                
        chunks = []
        async for chunk in violating_stream("Tell me about external data"):
            chunks.append(chunk)
            
        full_text = "".join(chunks)
        self.assertIn("[SIA INTERCEPTED]", full_text)
        self.assertNotIn("stream.", full_text)

if __name__ == "__main__":
    unittest.main()
