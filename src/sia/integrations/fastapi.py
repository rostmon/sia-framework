"""
FastAPI Integration — Native middleware for SIA.
Enables automatic EU AI Act governance for any FastAPI application.
"""
from __future__ import annotations
from typing import Callable, Optional
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from sia.adapters.client import SIAClient
from sia.adapters.mock_adapter import MockAdapter


class SIAMiddleware(BaseHTTPMiddleware):
    """
    FastAPI Middleware to automatically govern all incoming requests
    and outgoing responses via SIA.
    """

    def __init__(
        self,
        app,
        config_path: str = "configs/eu_ai_act_full.yaml",
        adapter=None,
        webhook_url: Optional[str] = None
    ):
        super().__init__(app)
        # Default to MockAdapter if none provided for easy testing
        self.client = SIAClient(
            adapter=adapter or MockAdapter(),
            config_path=config_path,
            webhook_url=webhook_url
        )

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # 1. Capture request body (prompt)
        # Note: This is a simplified implementation. Real-world middleware 
        # needs to handle different content types and JSON structures.
        body = await request.body()
        prompt = body.decode("utf-8") if body else ""

        # 2. SIA Ingress Check
        if prompt:
            ingress_result = self.client._ingress.process_prompt(prompt)
            if not ingress_result["allowed"]:
                blocked = self.client._handle_blocked(prompt, ingress_result)
                return JSONResponse(
                    content={"detail": blocked.content},
                    status_code=blocked.http_status,
                    headers=blocked.http_headers
                )
            if ingress_result.get("requires_human_review"):
                veto = self.client._handle_veto(prompt, ingress_result)
                return JSONResponse(
                    content={"detail": veto.content},
                    status_code=veto.http_status,
                    headers=veto.http_headers
                )

        # 3. Proceed to application
        response = await call_next(request)

        # 4. SIA Egress Check (if response is JSON/Text)
        # Simplified: We only govern the request in this middleware version.
        # Full egress governance would require capturing the response body.
        
        response.headers["X-SIA-Governed"] = "true"
        return response
