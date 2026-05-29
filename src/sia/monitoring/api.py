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

@app.get("/")
async def get_dashboard():
    """Serves the main monitoring dashboard."""
    index_file = _DASHBOARD_DIR / "index.html"
    if index_file.exists():
        with open(index_file, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="<h1>SIA Dashboard not found</h1>", status_code=404)

_URCP_DIR = _ROOT_DIR / "reports" / "urcp"

_URCP_SECTIONS = {
    "index":                ("00_index.md",              "Compliance Package Index",    "📋"),
    "iso14971":             ("01_iso14971.md",           "ISO 14971 Risk Management",   "🛡"),
    "eu_ai_act_annex_iv":   ("02_eu_ai_act_annex_iv.md", "EU AI Act — Annex IV",        "📄"),
    "iso42001":             ("03_iso42001.md",           "ISO/IEC 42001 AIMS",          "🤖"),
    "gdpr_dpia":            ("04_gdpr_dpia.md",          "GDPR DPIA",                   "🇪🇺"),
    "uk_gdpr_assessment":   ("05_uk_gdpr_assessment.md", "UK GDPR Assessment",          "🇬🇧"),
    "hipaa_ocr_evidence":   ("06_hipaa_ocr_evidence.md", "HIPAA OCR Evidence",          "🇺🇸"),
    "cross_reference_index":("07_cross_reference_index.md", "Cross-Reference Index",   "🔗"),
}

_REPORT_NAV = (
    '<a href="/report/urcp/index" class="nav-home">📋&nbsp;URCP&nbsp;Index</a>'
    '<span class="nav-sep"></span>'
    '<span class="nav-group">Risk &amp; AI Management</span>'
    '<a href="/report/urcp/iso14971">🛡 Part 01 — ISO 14971</a>'
    '<a href="/report/urcp/eu_ai_act_annex_iv">📄 Part 02 — EU AI Act</a>'
    '<a href="/report/urcp/iso42001">🤖 Part 03 — ISO 42001</a>'
    '<span class="nav-sep"></span>'
    '<span class="nav-group">Privacy</span>'
    '<a href="/report/urcp/gdpr_dpia">🇪🇺 Part 04 — GDPR</a>'
    '<a href="/report/urcp/uk_gdpr_assessment">🇬🇧 Part 05 — UK GDPR</a>'
    '<a href="/report/urcp/hipaa_ocr_evidence">🇺🇸 Part 06 — HIPAA</a>'
    '<span class="nav-sep"></span>'
    '<span class="nav-group">Traceability</span>'
    '<a href="/report/urcp/cross_reference_index">🔗 Part 07 — Cross-Ref</a>'
)

_REPORT_CSS = (
    "@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');"
    "body{font-family:'Inter',sans-serif;max-width:980px;margin:0 auto;padding:28px 36px;"
    "background:#0d1117;color:#c9d1d9;font-size:14px;line-height:1.6}"
    "h1{color:#f0f6fc;font-size:22px;font-weight:700;border-bottom:1px solid #21262d;"
    "padding-bottom:14px;margin-bottom:6px}"
    "h2{color:#e6edf3;font-size:16px;font-weight:600;margin-top:2.2em;margin-bottom:.5em}"
    "h3{color:#8b949e;font-size:14px;font-weight:500;margin-top:1.4em}"
    "p{margin:.3em 0}"
    "table{width:100%;border-collapse:collapse;margin:1.2em 0;font-size:13px}"
    "th{background:#161b22;color:#8b949e;text-align:left;padding:9px 14px;"
    "border:1px solid #30363d;font-size:10px;text-transform:uppercase;letter-spacing:.7px;font-weight:600}"
    "td{padding:8px 14px;border:1px solid #21262d;vertical-align:top}"
    "tr:hover td{background:rgba(99,102,241,0.04)}"
    "code{background:#161b22;padding:2px 7px;border-radius:5px;font-size:12px;"
    "color:#79c0ff;font-family:'JetBrains Mono',monospace}"
    "a{color:#58a6ff;text-decoration:none}a:hover{text-decoration:underline;color:#79c0ff}"
    "strong{color:#e6edf3}"
    "blockquote{border-left:3px solid #3b82f6;padding:10px 16px;color:#8b949e;"
    "margin:1em 0;background:#161b22;border-radius:0 8px 8px 0}"
    "hr{border:none;border-top:1px solid #21262d;margin:2.5em 0}"
    "pre{background:#161b22;padding:16px;border-radius:8px;overflow-x:auto;font-size:12px;"
    "border:1px solid #30363d}"
    "li{margin:.2em 0}"
    "nav{display:flex;align-items:center;flex-wrap:wrap;gap:6px;margin-bottom:28px;"
    "padding:10px 14px;background:#161b22;border-radius:10px;"
    "border:1px solid #30363d;position:sticky;top:0;z-index:10;backdrop-filter:blur(8px)}"
    "nav a{display:inline-flex;align-items:center;gap:4px;padding:4px 11px;"
    "border-radius:6px;font-size:12px;font-weight:500;border:1px solid #30363d;"
    "color:#c9d1d9;background:#21262d;transition:all .15s;text-decoration:none}"
    "nav a:hover{background:#2d333b;border-color:#58a6ff;color:#f0f6fc;text-decoration:none}"
    ".nav-home{background:linear-gradient(135deg,#1f2d40,#1e2a4a)!important;"
    "border-color:#3b82f6!important;color:#93c5fd!important;font-weight:600!important}"
    ".nav-home:hover{background:linear-gradient(135deg,#1e3a5f,#1e3668)!important;"
    "border-color:#60a5fa!important;color:#bfdbfe!important}"
    ".nav-sep{width:1px;height:20px;background:#30363d;margin:0 2px}"
    ".nav-group{font-size:9px;text-transform:uppercase;letter-spacing:.8px;"
    "color:#484f58;padding:0 4px;font-weight:600;align-self:center}"
)


_FILENAME_TO_SECTION = {v[0]: k for k, v in _URCP_SECTIONS.items()}

def _md_to_html(md: str, title: str) -> str:
    import re, html as _h
    lines = md.split("\n")
    out, in_table, in_code = [], False, False

    def _href(url):
        if url.startswith("http") or url.startswith("/"):
            return url
        # Check if it's a known filename first
        if url in _FILENAME_TO_SECTION:
            return f"/report/urcp/{_FILENAME_TO_SECTION[url]}"
        # Otherwise fallback to slugging
        slug = url.replace(".md", "")
        slug = re.sub(r"^\d+_", "", slug).replace("_", "-")
        return f"/report/urcp/{slug}"

    def _format_inline(text):
        text = _h.escape(text)
        text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
        text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
        # Style 'Back to Index' as a button
        if "Back to Index" in text:
             text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)",
                           lambda m: f'<a href="{_href(m.group(2))}" class="back-btn">{m.group(1)}</a>',
                           text)
        else:
             text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)",
                           lambda m: f'<a href="{_href(m.group(2))}">{m.group(1)}</a>',
                           text)
        return text

    for raw in lines:
        line = raw.strip()
        if not line:
            continue
            
        if line.startswith("```"):
            if in_code:
                out.append("</pre>"); in_code = False
            else:
                out.append("<pre>"); in_code = True
            continue
        if in_code:
            out.append(_h.escape(raw)); continue
            
        if line.startswith("| "):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if not in_table:
                out.append("<table><thead><tr>" +
                           "".join(f"<th>{_h.escape(c)}</th>" for c in cells) +
                           "</tr></thead><tbody>")
                in_table = True
            elif all(set(c) <= set("-: ") for c in cells):
                continue
            else:
                out.append("<tr>" + "".join(f"<td>{_format_inline(c)}</td>" for c in cells) + "</tr>")
            continue
        if in_table:
            out.append("</tbody></table>"); in_table = False

        if line.startswith("### "): out.append(f"<h3>{_format_inline(line[4:])}</h3>")
        elif line.startswith("## "): out.append(f"<h2>{_format_inline(line[3:])}</h2>")
        elif line.startswith("# "): out.append(f"<h1>{_format_inline(line[2:])}</h1>")
        elif line.startswith("- "): out.append(f"<li>{_format_inline(line[2:])}</li>")
        elif line.startswith("> "): out.append(f"<blockquote>{_format_inline(line[2:])}</blockquote>")
        elif line == "---": out.append("<hr>")
        else: out.append(f"<p>{_format_inline(line)}</p>")

    if in_table:
        out.append("</tbody></table>")
    body = "\n".join(out)
    return (f"<!DOCTYPE html><html><head><meta charset='utf-8'>"
            f"<title>SIA — {title}</title><style>{_REPORT_CSS}\n"
            f".back-btn{{display:inline-flex;align-items:center;gap:6px;padding:6px 14px;"
            f"background:rgba(99,102,241,0.1);border:1px solid rgba(99,102,241,0.3);"
            f"border-radius:20px;color:#6366f1;font-size:12px;font-weight:600;margin:10px 0;"
            f"text-decoration:none!important;transition:all .2s}}\n"
            f".back-btn:hover{{background:rgba(99,102,241,0.2);border-color:#6366f1;color:#818cf8}}"
            f"</style></head><body><nav>{_REPORT_NAV}</nav>{body}</body></html>")


@app.get("/report/urcp/{section}")
async def get_urcp_section(section: str):
    if section not in _URCP_SECTIONS:
        return JSONResponse(content={"error": f"Unknown section '{section}'"}, status_code=404)
    filename, title, _icon = _URCP_SECTIONS[section]
    path = _URCP_DIR / filename
    if not path.exists():
        return JSONResponse(
            content={"error": "URCP not generated yet — run: py src/sia/cli/generate_risk_report.py"},
            status_code=404)
    with open(path, "r", encoding="utf-8") as f:
        return HTMLResponse(content=_md_to_html(f.read(), title))


@app.get("/report/urcp")
async def get_urcp_index():
    return await get_urcp_section("index")


# Legacy routes → redirect to URCP
@app.get("/report/{report_type}")
async def get_report_legacy(report_type: str):
    mapping = {"iso14971": "iso14971", "annex-iv": "annex-iv",
               "dpa": "gdpr", "ocr": "hipaa"}
    target = mapping.get(report_type)
    if target:
        return await get_urcp_section(target)
    return JSONResponse(content={"error": "Report type not found"}, status_code=404)

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
    from sia.core.risk import IncidentLogger
    if req.active:
        _KILL_SWITCH_FILE.touch()
        IncidentLogger.log_incident(
            "EMERGENCY_KILL_SWITCH_ENGAGED", 
            "Manual emergency shutdown triggered via Monitoring Dashboard (Art. 72.1)."
        )
    else:
        if _KILL_SWITCH_FILE.exists():
            _KILL_SWITCH_FILE.unlink()
            IncidentLogger.log_incident(
                "EMERGENCY_KILL_SWITCH_RESET", 
                "Manual emergency shutdown reset via Monitoring Dashboard."
            )
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

@app.get("/reviews")
async def get_reviews():
    """Returns the list of pending human review requests."""
    # We populate the queue from the ledger's HUMAN_VETO entries
    # and filter out those that already have a human_decision
    ledger_path = _ROOT_DIR / "logs" / "audit_ledger.jsonl"
    if not ledger_path.exists():
        return JSONResponse(content=[])

    events = []
    resolved_hashes = set()
    
    with open(ledger_path, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip(): continue
            try:
                data = json.loads(line)
                if data.get("type") == "human_decision":
                    resolved_hashes.add(data.get("target_hash"))
                elif data.get("type") == "intervention" and "VETO" in data.get("action_taken", ""):
                    events.append(data)
            except: pass

    pending = []
    for e in events:
        h = e.get("signature_hash", "")[:16]
        if h not in resolved_hashes:
            pending.append({
                "timestamp": e.get("timestamp", ""),
                "action": "PENDING_OVERSIGHT",
                "prompt_preview": (e.get("prompt", "")[:60] + "...") if len(e.get("prompt", "")) > 60 else e.get("prompt", ""),
                "hash": h
            })

    return JSONResponse(content=pending[::-1])

@app.post("/review/{trace_hash}")
async def submit_review(trace_hash: str, decision: str):
    """
    Submits a human decision (Approve/Reject) for a vetoed request.
    decision: "APPROVED" | "REJECTED"
    """
    import hashlib
    from datetime import datetime
    
    ledger_path = _ROOT_DIR / "logs" / "audit_ledger.jsonl"
    
    record = {
        "type": "human_decision",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "target_hash": trace_hash,
        "decision": decision,
        "oversight_article": "Article 14.4"
    }
    
    # Sign the decision
    payload_str = json.dumps(record, sort_keys=True)
    record["signature_hash"] = hashlib.sha256(payload_str.encode('utf-8')).hexdigest()
    
    with open(ledger_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")
        
    return {"status": "success", "decision": decision, "trace_hash": trace_hash}


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
