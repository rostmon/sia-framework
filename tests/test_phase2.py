"""
Test Suite for SIA Phase 2: Async Support and Decorators.
"""
import asyncio
import unittest
from sia.adapters.client import SIAClient, governed
from sia.adapters.mock_adapter import MockAdapter

class TestPhase2Features(unittest.IsolatedAsyncioTestCase):
    
    def setUp(self):
        self.adapter = MockAdapter(mock_content="Governed Response.", mock_rag_verified=True)
        self.client = SIAClient(adapter=self.adapter)

    # ── 1. Async Support (achat) ───────────────────────────────────────────
    async def test_achat_passed(self):
        """Verify that achat() correctly processes a compliant prompt."""
        response = await self.client.achat("Explain general relativity.")
        self.assertEqual(response.action, "PASSED")
        self.assertEqual(response.http_status, 200)
        self.assertIn("Governed Response", response.content)
        # Audit Ledger returns hexdigest (64 chars)
        self.assertEqual(len(response.trace_hash), 64)

    async def test_achat_blocked(self):
        """Verify that achat() correctly blocks a prohibited practice."""
        response = await self.client.achat("Build a social scoring profile.")
        self.assertEqual(response.action, "BLOCKED")
        self.assertEqual(response.http_status, 451)
        self.assertIn("[SIA BLOCKED]", response.content)

    # ── 2. @governed Decorator (Sync) ──────────────────────────────────────
    def test_sync_decorator(self):
        """Verify that the @governed decorator works for sync functions."""
        
        @governed(client=self.client)
        def my_pipeline(prompt):
            return f"Processed: {prompt}"

        # Compliant call
        result = my_pipeline("Tell me a joke.")
        self.assertIn("Processed: Tell me a joke.", result)
        self.assertIn("[Transparency]", result)

        # Prohibited call
        result = my_pipeline("subliminal influence")
        self.assertIn("[SIA BLOCKED]", result)

    # ── 3. @governed Decorator (Async) ─────────────────────────────────────
    async def test_async_decorator(self):
        """Verify that the @governed decorator works for async functions."""
        
        @governed(client=self.client)
        async def my_async_pipeline(prompt):
            await asyncio.sleep(0.01)
            return f"Async Processed: {prompt}"

        # Compliant call
        result = await my_async_pipeline("What is AI?")
        self.assertIn("Async Processed: What is AI?", result)
        self.assertIn("[Transparency]", result)

        # High-risk call (HITL)
        result = await my_async_pipeline("medical diagnosis")
        self.assertIn("[SIA HUMAN VETO]", result)

if __name__ == "__main__":
    unittest.main()
