"""
SIA Monitoring API — FastAPI server exposing live metrics for the dashboard.

Run:  python -m sia.monitoring.api
      (then open dashboard/index.html in a browser)
"""
import asyncio
import sys
from pathlib import Path

# Ensure src/ is on path when run directly
sys.path.insert(0, str(Path(__file__).parents[4] / "src"))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from sia.monitoring.metrics_collector import MetricsCollector

app = FastAPI(
    title="SIA Governance Monitoring API",
    description="Real-time EU AI Act compliance monitoring for the SIA Framework",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

collector = MetricsCollector(ledger_path="logs/audit_ledger.jsonl")


@app.get("/health")
async def health():
    return {"status": "ok", "service": "SIA Monitoring API"}


@app.get("/metrics")
async def get_metrics():
    return JSONResponse(content=collector.compute())


@app.get("/metrics/summary")
async def get_summary():
    return JSONResponse(content=collector.compute()["summary"])


@app.get("/metrics/timeseries")
async def get_timeseries():
    return JSONResponse(content=collector.compute()["timeseries"])


@app.get("/audit-log")
async def get_audit_log():
    return JSONResponse(content=collector.compute()["recent_events"])


if __name__ == "__main__":
    uvicorn.run("sia.monitoring.api:app", host="127.0.0.1", port=8001, reload=True)
