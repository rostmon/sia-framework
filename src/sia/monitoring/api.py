"""
SIA Monitoring API — FastAPI server with WebSocket support for real-time streaming.

Run:  python -m uvicorn sia.monitoring.api:app --host 127.0.0.1 --port 8001
      Then open:  http://127.0.0.1:8001
"""
import sys
import asyncio
import json
from pathlib import Path
from typing import Set

sys.path.insert(0, str(Path(__file__).parents[4] / "src"))

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
import uvicorn

from sia.monitoring.metrics_collector import MetricsCollector

app = FastAPI(
    title="SIA Governance Monitoring API",
    description="Real-time EU AI Act compliance monitoring for the SIA Framework",
    version="1.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

_DASHBOARD_DIR = Path(__file__).parents[4] / "dashboard"
collector = MetricsCollector(ledger_path="logs/audit_ledger.jsonl")

# --- WebSocket Management ---
class ConnectionManager:
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        if not self.active_connections:
            return
        msg_str = json.dumps(message)
        await asyncio.gather(
            *[connection.send_text(msg_str) for connection in self.active_connections],
            return_exceptions=True
        )

manager = ConnectionManager()

@app.get("/", response_class=HTMLResponse)
async def serve_dashboard():
    html_path = _DASHBOARD_DIR / "index.html"
    return HTMLResponse(content=html_path.read_text(encoding="utf-8"), status_code=200)

@app.websocket("/ws/metrics")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        # Initial push
        await websocket.send_text(json.dumps(collector.compute()))
        
        while True:
            # Keep connection alive and push updates every 2 seconds
            # In a real system, this would be triggered by file-system events (watchdog)
            await asyncio.sleep(2)
            await websocket.send_text(json.dumps(collector.compute()))
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.get("/health")
async def health():
    return {"status": "ok", "service": "SIA Monitoring API"}

@app.get("/metrics")
async def get_metrics():
    return JSONResponse(content=collector.compute())

if __name__ == "__main__":
    uvicorn.run("sia.monitoring.api:app", host="127.0.0.1", port=8001, reload=True)
