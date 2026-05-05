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

# Robustly find the project root (sia-framework)
_CURRENT = Path(__file__).resolve().parent
while _CURRENT.name != "sia-framework" and _CURRENT.parent != _CURRENT:
    _CURRENT = _CURRENT.parent
_ROOT_DIR = _CURRENT

sys.path.insert(0, str(_ROOT_DIR / "src"))

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
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

_DASHBOARD_DIR = _ROOT_DIR / "dashboard"
collector = MetricsCollector(ledger_path=str(_ROOT_DIR / "logs" / "audit_ledger.jsonl"))

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

# In-memory review queue for demo purposes
# In production, this would be backed by a database
review_queue = []

@app.get("/reviews")
async def get_reviews():
    """Returns the list of pending human review requests."""
    # We populate the queue from the ledger's HUMAN_VETO entries
    metrics = collector.compute()
    recent = metrics.get("recent_events", [])
    pending = [e for e in recent if "VETO" in e["action"]]
    return JSONResponse(content=pending)

# --- Runtime Risk Management (Articles 9 & 72) ---

class KillSwitchRequest(BaseModel):
    active: bool

_KILL_SWITCH_FILE = _ROOT_DIR / "logs" / "kill_switch.flag"

@app.post("/admin/kill-switch")
async def toggle_kill_switch(req: KillSwitchRequest):
    """Toggles the global emergency kill-switch (file-based signal)."""
    if req.active:
        _KILL_SWITCH_FILE.touch()
    else:
        if _KILL_SWITCH_FILE.exists():
            _KILL_SWITCH_FILE.unlink()
    return {"status": "success", "kill_switch_active": req.active}

@app.get("/incidents")
async def get_incidents():
    """Returns Automated Incident Detection logs for Post-Market Monitoring."""
    incident_file = _ROOT_DIR / "logs" / "incident_ledger.jsonl"
    incidents = []
    if incident_file.exists():
        with open(incident_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    try:
                        incidents.append(json.loads(line))
                    except json.JSONDecodeError:
                        pass
    # Return last 50 incidents, newest first
    return JSONResponse(content=incidents[-50:][::-1])


from sia.regulatory.conformity import ConformityAssessor

# Initialize conformity assessor
assessor = ConformityAssessor(
    config_path=_ROOT_DIR / "configs" / "conformity_checklist.yaml",
    state_path=_ROOT_DIR / "logs" / "conformity_state.json"
)

@app.get("/conformity")
async def get_conformity_status():
    """Returns the current progress of the conformity assessment."""
    return JSONResponse(content=assessor.get_progress())

@app.post("/conformity/check")
async def update_conformity_check(req_id: str, check_id: str, completed: bool):
    """Updates the status of a specific conformity check."""
    assessor.update_check(req_id, check_id, completed)
    return {"status": "success", "progress": assessor.get_progress()["overall_percent"]}

@app.post("/review/{trace_hash}")
async def submit_review(trace_hash: str, decision: str):
    """
    Submits a human decision (Approve/Reject) for a vetoed request.
    decision: "APPROVED" | "REJECTED"
    """
    # Logic to update the ledger/audit trail would go here
    return {"status": "success", "decision": decision, "trace_hash": trace_hash}

from sia.regulatory.certificates import ConformityCertificate

@app.get("/report/conformity-certificate", response_class=HTMLResponse)
async def generate_conformity_certificate():
    """Generates a signed conformity certificate."""
    progress = assessor.get_progress()
    cert_gen = ConformityCertificate(project_name="SIA Framework Demo")
    cert_data = cert_gen.generate(progress)
    report_md = cert_gen.to_markdown(cert_data)
    return HTMLResponse(content=f"<pre>{report_md}</pre>", status_code=200)

@app.get("/report/annex-iv", response_class=HTMLResponse)
async def generate_annex_iv_report():
    """Generates an automated Annex IV Technical Documentation evidence report."""
    metrics = collector.compute()
    summary = metrics.get("summary", {})
    incident_file = _ROOT_DIR / "logs" / "incident_ledger.jsonl"
    incident_count = 0
    if incident_file.exists():
        with open(incident_file, "r", encoding="utf-8") as f:
            incident_count = sum(1 for line in f if line.strip())

    report = f"""# Automated Annex IV Compliance Evidence Report
*Generated by Sovereign Systemic Integrity Architecture (SIA) at {metrics.get("generated_at")}*

## 1. System Overview
- **Total Inferences Evaluated**: {summary.get("total_requests", 0)}
- **Overall Compliance Rate**: {summary.get("compliance_rate", 0)}%
- **Average Confidence Score**: {summary.get("avg_confidence", 0)}

## 2. Article 5 (Prohibited Practices)
- **Prohibited Practices Blocked**: {metrics.get("action_distribution", {}).get("BLOCKED", 0)} instances intercepted and dropped.

## 3. Article 10 (Data Governance)
- **PII Sanitization Events**: {summary.get("pii_redactions", 0)} instances redacted.

## 4. Article 14 (Human Oversight)
- **Human Veto Gates Triggered (HTTP 202)**: {summary.get("human_veto", 0)} instances flagged for human review.

## 5. Article 15 (Accuracy & Cybersecurity)
- **Hallucinations/Issues Rewritten**: {summary.get("rewritten", 0)} instances intercepted and modified by safety fallback.

## 6. Article 72 (Post-Market Monitoring)
- **Automated Risk Incidents Detected**: {incident_count} anomalies (e.g. Data Poisoning, Rate Limits, Drift) actively detected and mitigated in production.

## 7. Article 12 (Traceability) Cryptographic Ledger
Below is a sampled audit trail of the most recent cryptographic signatures anchoring these events to the immutable ledger:

| Timestamp | Action | Article Trigger | SHA-256 Signature Hash |
| :--- | :--- | :--- | :--- |
"""
    for event in metrics.get("recent_events", [])[:10]:
        report += f"| {event['timestamp']} | {event['action']} | {event['article']} | `{event['hash']}...` |\n"
        
    return HTMLResponse(content=f"<pre>{report}</pre>", status_code=200)

@app.get("/report/iso14971", response_class=HTMLResponse)
async def get_iso14971_report():
    """Returns the static ISO 14971 Risk Management Report with dynamic Post-Market Monitoring."""
    report_path = _ROOT_DIR / "reports" / "ISO14971_risk_management_report.md"
    if not report_path.exists():
        return HTMLResponse(content="Error: Static report not found.", status_code=500)
        
    content = report_path.read_text(encoding="utf-8")
    
    # Append dynamic Post-Market Monitoring (Article 72) Alerts
    content += "\n## 5. Post-Market Monitoring (Article 72) Alerts\n"
    content += "This section dynamically documents runtime Risk Management Alerts traceable to the Hazard Matrix above.\n\n"
    content += "| Timestamp | Incident Type | Details | Traceable Hazard |\n"
    content += "| --- | --- | --- | --- |\n"
    
    incident_file = _ROOT_DIR / "logs" / "incident_ledger.jsonl"
    if incident_file.exists():
        with open(incident_file, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip(): continue
                try:
                    data = json.loads(line)
                    t_stamp = data.get("timestamp", "")
                    if isinstance(t_stamp, float):
                        from datetime import datetime
                        t_stamp = datetime.fromtimestamp(t_stamp).strftime('%Y-%m-%d %H:%M:%S')
                    i_type = data.get("incident_type", "")
                    details = data.get("details", "")
                    
                    # Basic mapping to HZ ID
                    hz_id = "HZ-Unknown"
                    if "ANOMALY" in i_type: hz_id = "HZ-08"
                    elif "RATE_LIMIT" in i_type: hz_id = "HZ-11"
                    elif "LOW_CONFIDENCE" in i_type: hz_id = "HZ-06"
                    elif "DRIFT" in i_type: hz_id = "HZ-05"
                    elif "POISON" in i_type: hz_id = "HZ-08"
                    elif "KILL_SWITCH" in i_type: hz_id = "HZ-08"
                    
                    content += f"| {t_stamp} | `{i_type}` | {details} | **{hz_id}** |\n"
                except Exception as e:
                    pass

    return HTMLResponse(content=f"<pre style='font-family: Inter, sans-serif; white-space: pre-wrap; padding: 20px; color: #e2e8f0; background: #0a0d14;'>{content}</pre>", status_code=200)


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8015)
