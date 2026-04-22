"""
Webhooks Module — Standardized dispatcher for governance interventions (Art. 14.4).
Allows SIA to notify external human-in-the-loop (HITL) systems.
"""
import json
import logging
import asyncio
from typing import Any, Dict, Optional

try:
    import httpx
except ImportError:
    httpx = None

logger = logging.getLogger(__name__)

class WebhookDispatcher:
    """
    Dispatches notifications to external endpoints when governance gates 
    require human intervention (Article 14.4).
    """

    def __init__(self, webhook_url: Optional[str] = None):
        self.webhook_url = webhook_url

    async def notify_intervention(self, prompt: str, article: str, trace_hash: str, context: Dict[str, Any]):
        """
        Sends an asynchronous POST request to the configured webhook URL.
        """
        if not self.webhook_url:
            logger.info(f"No webhook configured. Intervention logged locally for trace {trace_hash}")
            return

        if not httpx:
            logger.warning("httpx not installed. Cannot dispatch webhook. Run: pip install httpx")
            return

        payload = {
            "event": "GOVERNANCE_INTERVENTION_REQUIRED",
            "article": article,
            "trace_hash": trace_hash,
            "prompt_preview": prompt[:200],
            "context": context,
            "system": "SIA-Framework-v1"
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.webhook_url,
                    json=payload,
                    timeout=5.0
                )
                response.raise_for_status()
                logger.info(f"Webhook dispatched successfully for {trace_hash}")
        except Exception as e:
            logger.error(f"Failed to dispatch webhook: {e}")

    def notify_intervention_sync(self, prompt: str, article: str, trace_hash: str, context: Dict[str, Any]):
        """Sync wrapper for the async notification."""
        if not self.webhook_url:
            return
        
        try:
            # We don't want to block the main thread too much, but for sync calls we must
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If we are in an async environment already, just schedule it
                asyncio.create_task(self.notify_intervention(prompt, article, trace_hash, context))
            else:
                asyncio.run(self.notify_intervention(prompt, article, trace_hash, context))
        except Exception as e:
            logger.error(f"Sync webhook dispatch error: {e}")
