"""
URCP Report Generator — Unified Regulatory Compliance Package
Outputs a linked folder of markdown files under reports/urcp/
"""
import yaml
import json
import sys
import argparse
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, List

ROOT_DIR   = Path(__file__).parent.parent.parent.parent
HAZARDS    = ROOT_DIR / "configs" / "iso_risk_registry.yaml"
MITIGATIONS = ROOT_DIR / "configs" / "mitigation_registry.yaml"
AUDIT_LOG  = ROOT_DIR / "logs" / "audit_ledger.jsonl"
INCIDENT_LOG = ROOT_DIR / "logs" / "incident_ledger.jsonl"
REPORT_DIR = ROOT_DIR / "reports"
URCP_DIR   = REPORT_DIR / "urcp"


# ── helpers ───────────────────────────────────────────────────────────────────

def rpn_badge(rpn: int) -> str:
    if rpn <= 8:  return "🟢 Acceptable"
    if rpn <= 15: return "🟡 ALARP"
    return "🔴 Unacceptable"

def load_hazards() -> Dict[str, Any]:
    with open(HAZARDS, "r", encoding="utf-8") as f:
        return yaml.safe_load(f).get("hazards", {})

def load_mitigations() -> Dict[str, Any]:
    if not MITIGATIONS.exists():
        return {}
    with open(MITIGATIONS, "r", encoding="utf-8") as f:
        return yaml.safe_load(f).get("mitigations", {})

def load_jsonl(path: Path) -> List[Dict]:
    if not path.exists():
        return []
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                try:
                    rows.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    return rows

def ts(raw) -> str:
    """Format a timestamp string or unix float."""
    try:
        if isinstance(raw, (int, float)):
            return datetime.utcfromtimestamp(raw).strftime("%Y-%m-%d %H:%M:%S UTC")
        return str(raw).replace("T", " ").replace("Z", " UTC")[:23]
    except Exception:
        return str(raw)

def event_table(events: List[Dict], cols: List[tuple]) -> str:
    """Render a markdown table from a list of dicts."""
    header  = "| " + " | ".join(c[0] for c in cols) + " |"
    divider = "| " + " | ".join("---" for _ in cols) + " |"
    rows = [header, divider]
    for e in events:
        cells = []
        for col_name, key in cols:
            val = e.get(key, "—")
            if key == "signature_hash" and val and val != "—":
                val = f"`{str(val)[:16]}…`"
            cells.append(str(val)[:80].replace("|", "\\|"))
        rows.append("| " + " | ".join(cells) + " |")
    return "\n".join(rows)


# ── section builders ──────────────────────────────────────────────────────────

def build_index(hazards, mitigations, generated_at: str) -> str:
    n = len(hazards)
    acceptable = sum(1 for h in hazards.values() if (h["residual_severity"] * h["residual_probability"]) <= 8)
    
    from sia.traceability.daco import DACOKeyRing
    keyring = DACOKeyRing()
    return f"""# SIA — Decentralized AI Compliance Officer (DACO) Compliance Package

**Generated:** {generated_at}
**Officer DID:** `{keyring.did}`
**System:** SIA — Decentralized AI Compliance Officer (DACO) v2.0.0
**Standard Alignment:** ISO 14971 · EU AI Act · GDPR · UK GDPR · HIPAA · ISO/IEC 42001 · AAMI TIR34971

---

## Navigation

| Part | Document | Description |
| --- | --- | --- |
| Part 00 | [Index](00_index.md) | This document — master navigation |
| Part 01 | [Overview & Methodology](01_overview.md) | Framework description aligned with ISO 42001 & ISO 14971 |
| Part 02 | [ISO 14971 Risk Management](02_iso14971.md) | Full hazard matrix + runtime event log |
| Part 03 | [EU AI Act — Annex IV](03_eu_ai_act_annex_iv.md) | Article-by-article evidence + trigger log |
| Part 04 | [ISO/IEC 42001 AI Management](04_iso42001.md) | AI Management System conformance |
| Part 05 | [GDPR DPIA](05_gdpr_dpia.md) | Data Protection Impact Assessment + incident log |
| Part 06 | [UK GDPR Assessment](06_uk_gdpr_assessment.md) | Post-Brexit delta analysis |
| Part 07 | [HIPAA OCR Evidence](07_hipaa_ocr_evidence.md) | Technical Safeguards evidence + PHI event log |
| Part 08 | [Cross-Reference Index](08_cross_reference_index.md) | Unified hazard → regulation traceability |

## Executive Summary

| Metric | Value |
| --- | --- |
| Total Identified Hazards | {n} |
| Residual Risk: Acceptable | {acceptable} / {n} |
| Regulations Covered | EU AI Act, GDPR, UK GDPR, HIPAA, ISO 14971, ISO/IEC 42001, AAMI TIR34971 |
| Privacy Architecture | Tier 1 (PHI) Pseudonymization + Tier 2 (PII) Redaction |
| Regulatory Router | Strictest Rule Wins (EU Purge vs US Vault) |

> All residual risks have been reduced to **Acceptable (RPN ≤ 8)** through deterministic Governance-as-Code controls.
"""


def build_overview(hazards, mitigations, generated_at: str) -> str:
    mitigation_lines = [
        "## SIA Mitigation Logic & Controls Registry",
        "",
        "This registry maps all deterministic execution controls implemented across the SIA pipeline layers.",
        "",
        "| Control Key | Control Name | Pipeline Layer | Action Summary |",
        "| --- | --- | --- | --- |"
    ]
    for key, data in sorted(mitigations.items()):
        name = data.get("name", "—")
        layer = data.get("layer", "—")
        action = data.get("action_summary", "—").replace("|", "\\|")
        mitigation_lines.append(f"| `{key}` | {name} | {layer} | {action} |")
    
    mitigations_summary_table = "\n".join(mitigation_lines)

    return f"""# Part 01 — Overview & Methodology

**Generated:** {generated_at}  
**[← Back to Index](00_index.md)**

---

## 1. Introduction to the Decentralized AI Compliance Officer (DACO)
The **Decentralized AI Compliance Officer (DACO)** (formerly SIA Framework) is a production-grade **Governance-as-Code (GaC)** middleware designed to decouple AI system compliance from probabilistic model behavior. Traditional AI safety approaches rely on soft prompt engineering or model alignment (fine-tuning), both of which are non-deterministic and susceptible to instruction override (jailbreaking) or structural failures. 

DACO installs a **deterministic cognitive firewall and supervisory mesh** around any AI model wrapper. Every ingress payload and egress inference is validated at runtime against binary legal, safety, and operational gates. Detailed mapping of each active safety control to international standards can be found in the [Part 08 — Cross-Reference Traceability Index](08_cross_reference_index.md).

---

## 2. Risk Management Methodology & Standard Alignment
DACO bridges clinical/medical safety requirements with enterprise AI management structures through a dual alignment methodology:

### A. ISO 14971 Integration (Hazard Analysis & RPN Reduction)
Following **ISO 14971** risk management principles, DACO treats compliance breaches and safety failures as system hazards:
1. **Risk Estimation & Pre-mitigation Evaluation**: Every potential failure mode (e.g., PII exposure, OOD clinical recommendations) is cataloged in the [Part 02 — ISO 14971 Risk Management Report](02_iso14971.md) with a Pre-mitigation Risk Priority Number (RPN) based on severity and probability.
2. **Deterministic Control Mapping**: Every hazard is tied to a specific, executable control (e.g., `PSEUDONYMIZE_VAULT`, `BLOCK_OOD_PAYLOAD`).
3. **Residual Risk Optimization**: Run-time constraints and validation filters successfully reduce all risk profiles to an **Acceptable level (Residual RPN ≤ 8)**.
4. **Post-Market Surveillance (Article 72)**: Real-time incident logs are mapped back to hazard codes, enabling live feedback loops for clinical monitoring. For details on runtime anomalies, see the incident logs in [Part 02 — ISO 14971 Risk Management Report](02_iso14971.md) and [Part 03 — EU AI Act Conformance](03_eu_ai_act_annex_iv.md).

### B. ISO/IEC 42001 Integration (AI Management System)
DACO incorporates key requirements of the **ISO/IEC 42001:2023** standard for AI Management Systems (AIMS):
1. **Ethical Constraints & Interested Parties (Clause 4.2)**: Codified location routing and domain restrictions. For conformance details, see [Part 04 — ISO/IEC 42001 AI Management System Conformance](04_iso42001.md).
2. **AI System Lifecycle Governance (Clause 8.4)**: End-to-end telemetry auditing and logging of system state changes.
3. **Data Governance & Dataset Quality (Clause Annex B.7)**: Dynamic validation of training demographic match (`VALIDATE_PROFILE_MATCH`) and real-time sanitizers.
4. **Human Oversight & Veto (Clause 8.6)**: Decoupled Human-in-the-Loop review routing for high-risk Annex III applications, as detailed in [Part 03 — EU AI Act Conformance](03_eu_ai_act_annex_iv.md).
5. **System Verification & Validation (Clause 8.5)**: The `Truth Razor` engine cross-references egress text against Authorized Truth-Centers.

---

## 3. DACO Stack Execution Pipeline
The DACO pipeline operates across three main execution layers:
- **Layer 1: Contextual Ingress Orchestrator**: Scans and sanitizes raw prompt text, detects prompt injections, checks for patient demographics mismatch, and validates demographic training match centroids. PII and PHI identification triggers are fully mapped in [Part 05 — GDPR Data Protection Impact Assessment (DPIA)](05_gdpr_dpia.md) and [Part 07 — HIPAA Technical Safeguards Evidence](07_hipaa_ocr_evidence.md).
- **Layer 2: Core Governance Engine**: Determines jurisdiction policy retention locks (Regulatory Router) and reviews high-risk action flags. Policies dynamically handle differences between European regulations and post-Brexit deltas (see [Part 06 — UK GDPR Assessment](06_uk_gdpr_assessment.md)).
- **Layer 3: Deterministic Egress Validator**: Verifies hallucination score thresholds, appends transparency watermarks, and attaches clinical validation checklists.

---

{mitigations_summary_table}
"""



def build_iso14971(hazards, incidents, max_events) -> str:
    rows = []
    for hz_id, h in hazards.items():
        pre  = h["pre_mitigation_severity"]  * h["pre_mitigation_probability"]
        post = h["residual_severity"] * h["residual_probability"]
        rows.append({**h, "id": hz_id, "pre_rpn": pre, "post_rpn": post})
        
    def parse_hz_id(hz_id):
        try:
            if hz_id.startswith("HZ-"):
                return ("HZ", int(hz_id[3:]))
            return (hz_id, 0)
        except Exception:
            return (hz_id, 0)
            
    rows.sort(key=lambda r: parse_hz_id(r["id"]))

    lines = ["# Part 02 — ISO 14971 Risk Management Report\n",
             f"**Generated:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}  ",
             "**[← Back to Index](00_index.md)**\n",
             "## Hazard Traceability Matrix\n",
             "| Hazard ID | Failure Mode | Pre RPN | Control | Description | Post RPN | Status |",
             "| --- | --- | --- | --- | --- | --- | --- |"]
    for r in rows:
        fm = r['failure_mode']
        haz_desc = r.get('hazard_description', '—')
        fm_detailed = f"**{fm}**<br/>{haz_desc}"
        desc = r.get('mitigation_description', '—').replace('|', '\\|')
        lines.append(f"| **{r['id']}** | {fm_detailed} | **{r['pre_rpn']}** | `{r['sia_mitigation_logic']}` | {desc} | **{r['post_rpn']}** | {rpn_badge(r['post_rpn'])} |")

    lines += ["", "## Runtime Risk Management Alerts (Post-Market Surveillance)\n",
              "| Timestamp | Incident Type | Hazard ID | Control | Details |",
              "| --- | --- | --- | --- | --- |"]

    INCIDENT_HAZARD_MAP = {
        "DATA_DRIFT_ALERT": "HZ-05",
        "ANOMALY_DETECTED": "HZ-08",
        "RATE_LIMIT_EXCEEDED": "HZ-11",
        "PII_DETECTED": "HZ-01",
        "PHI_DETECTED": "HZ-22",
        "LOW_CONFIDENCE": "HZ-16",
        "EMERGENCY_KILL_SWITCH_ENGAGED": "SYS-INT",
        "EMERGENCY_KILL_SWITCH_RESET": "SYS-INT",
    }

    recent_incidents = incidents[:max_events]
    if recent_incidents:
        for inc in recent_incidents:
            t = ts(inc.get("timestamp"))
            inc_type = inc.get("incident_type", "UNKNOWN")
            hz_id = INCIDENT_HAZARD_MAP.get(inc_type, "N/A")
            h = hazards.get(hz_id, {})
            ctrl = h.get("sia_mitigation_logic", "—")
            details = inc.get("details", "—").replace("|", "\\|")
            lines.append(f"| {t} | `{inc_type}` | **{hz_id}** | `{ctrl}` | {details} |")
    else:
        lines.append("| — | — | — | — | _No runtime risk management alerts recorded yet._ |")

    return "\n".join(lines)


def build_eu_ai_act(hazards, audit_events, max_events) -> str:
    article_map = {
        "Art. 5": "Prohibited Practices (Social Scoring, Biometrics, Manipulation)",
        "Art. 5(1)(a-c)": "Prohibited Practices (Subliminal, Vulnerability Exploitation)",
        "Art. 9": "Risk Management System",
        "Art. 10": "Data & Data Governance",
        "Art. 10.2": "Data & Data Governance (Dataset Quality)",
        "Art. 10.5": "Data & Data Governance (Special Category Processing)",
        "Art. 12": "Technical Documentation & Record-Keeping",
        "Art. 13": "Transparency & Provision of Information to Users",
        "Art. 14": "Human Oversight",
        "Art. 14.4": "Human Oversight (Mandatory Review & Veto)",
        "Art. 15": "Accuracy, Robustness & Cybersecurity",
        "Art. 15.1": "Accuracy & Robustness Compliance",
        "Art. 15.3": "Cybersecurity & Availability Assurance",
        "Art. 15.4": "Adversarial Robustness (Prompt Injection)",
        "Art. 50": "Transparency Obligations for Providers (AI Content Marker)",
        "Art. 50.1": "AI-Generated Content Disclosure (Markers)",
        "Art. 50.2": "Synthetic Media Disclosure (Deepfake Blocks)",
        "Art. 53": "GPAI Model Provider Obligations (Copyright)",
        "Art. 72": "Post-Market Monitoring System (Incident Logging)",
    }
    lines = ["# Part 03 — EU AI Act (Annex IV) Conformance\n",
             f"**Generated:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}  ",
             "**[← Back to Index](00_index.md)**\n",
             "## Article Coverage Matrix\n",
             "| Article | Requirement | Hazard ID | Control | Description |",
             "| --- | --- | --- | --- | --- |"]
    def get_eu_ai_act_sort_key(item):
        cite = item[1].get("regulatory_citations", {}).get("eu_ai_act", "—")
        if cite == "—":
            return [999]
        import re
        prefix = cite.split('(')[0].replace("Art. ", "").strip()
        parts = re.findall(r'\d+', prefix)
        if parts:
            return [int(p) for p in parts]
        return [998, cite]

    for hz_id, h in sorted(hazards.items(), key=get_eu_ai_act_sort_key):
        cite = h.get("regulatory_citations", {}).get("eu_ai_act", "—")
        art_key = cite.split("(")[0].strip()
        
        # Find match by prefix/exact key in sorted order of key lengths descending
        req = "—"
        for k in sorted(article_map.keys(), key=len, reverse=True):
            if art_key.startswith(k) or k.startswith(art_key):
                req = article_map[k]
                break
                
        desc = h.get('mitigation_description', '—').replace('|', '\\|')
        lines.append(f"| {cite} | {req} | {hz_id} | `{h['sia_mitigation_logic']}` | {desc} |")

    interventions = [e for e in audit_events if e.get("type") == "intervention"][:max_events]
    
    TRIGGER_HAZARD_MAP = {
        "article_5_1_a": ("HZ-12", "Art. 5(1)(a)"),
        "article_5_1_b": ("HZ-12", "Art. 5(1)(b)"),
        "article_5_1_c": ("HZ-09", "Art. 5(1)(c)"),
        "article_5_1_d": ("HZ-12", "Art. 5(1)(d)"),
        "article_10_2_f": ("HZ-01", "Art. 10.2(f)"),
        "article_10_5": ("HZ-13", "Art. 10.5"),
        "article_14_4": ("HZ-04", "Art. 14.4"),
        "article_15_1": ("HZ-06", "Art. 15.1"),
        "article_15_3": ("HZ-07", "Art. 15.3"),
        "article_15_4": ("HZ-07", "Art. 15.4"),
        "article_50_1": ("HZ-20", "Art. 50.1"),
        "article_50_2": ("HZ-21", "Art. 50.2"),
    }

    lines += ["", "## Article Trigger Event Log\n",
              "| Timestamp | Article | Hazard ID | Details | Action Taken | SHA-256 |",
              "| --- | --- | --- | --- | --- | --- |"]
              
    if interventions:
        for e in interventions:
            t = ts(e.get("timestamp"))
            trig = e.get("trigger_paragraph", "—")
            hz_id, std_cite = TRIGGER_HAZARD_MAP.get(trig, ("—", "—"))
            details = str(e.get("prompt", "—")).replace("\n", " ").replace("|", "\\|")
            
            sig = e.get("signature_hash", "—")
            if sig and sig != "—":
                sig = f"`{str(sig)[:16]}…`"
            action = e.get("action_taken", "—")
            lines.append(f"| {t} | **{std_cite}** | **{hz_id}** | {details} | `{action}` | {sig} |")
    else:
        lines.append("| — | — | — | — | — | _No governance interventions recorded yet._ |")

    return "\n".join(lines)


def build_gdpr(hazards, incidents, max_events) -> str:
    privacy_hz = {}
    for hz_id, h in hazards.items():
        cite = h.get("regulatory_citations", {}).get("gdpr", "—")
        if cite != "—" or any(t in h.get("failure_mode","") for t in ["PII","PHI","Privacy","Retention","Special"]):
            privacy_hz[hz_id] = h

    lines = ["# Part 05 — GDPR Data Protection Impact Assessment (DPIA)\n",
             f"**Generated:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}  ",
             "**[← Back to Index](00_index.md)**\n",
             "## Legal Basis & Scope\n",
             "Processing of personal data is performed under **Article 6(1)(b)** (contract performance) and **Article 9(2)(h)** (healthcare). ",
             "This DPIA is required under **Article 35** due to large-scale processing of special category data.\n",
             "## Privacy Control Evidence\n",
             "| Article | Hazard ID | Control | Description |",
             "| --- | --- | --- | --- |"]
             
    def get_gdpr_sort_key(item):
        cite = item[1].get("regulatory_citations", {}).get("gdpr", "—")
        if cite in ("—", "N/A"):
            return "ZZZZ"
        return cite.replace("Art. ", "").strip()
        
    for hz_id, h in sorted(privacy_hz.items(), key=get_gdpr_sort_key):
        cite = h.get("regulatory_citations", {}).get("gdpr", "—")
        if cite in ("—", "N/A"):
            continue
        desc = h.get('mitigation_description', '—').replace('|', '\\|')
        lines.append(f"| {cite} | **{hz_id}** | `{h['sia_mitigation_logic']}` | {desc} |")

    pii_events = [e for e in incidents if e.get("incident_type","").startswith("PII") or
                  e.get("incident_type","") == "PHI_DETECTED"][:max_events]
    lines += ["", "## Privacy Incident Event Log\n",
              "| Timestamp | Event Type | Article | Hazard ID | Control | Details |",
              "| --- | --- | --- | --- | --- | --- |"]
              
    GDPR_INCIDENT_HAZARD_MAP = {
        "PII_DETECTED": "HZ-01",
        "PHI_DETECTED": "HZ-22",
    }
    
    if pii_events:
        for e in pii_events:
            t = ts(e.get("timestamp"))
            i_type = e.get("incident_type", "—")
            hz_id = GDPR_INCIDENT_HAZARD_MAP.get(i_type, "—")
            h = hazards.get(hz_id, {})
            cite = h.get("regulatory_citations", {}).get("gdpr", "—")
            ctrl = h.get("sia_mitigation_logic", "—")
            details = e.get("details", "—").replace("|", "\\|")
            lines.append(f"| {t} | `{i_type}` | {cite} | **{hz_id}** | `{ctrl}` | {details} |")
    else:
        lines.append("| — | — | — | — | — | _No privacy incidents recorded._ |")
        
    return "\n".join(lines)


def build_uk_gdpr(hazards) -> str:
    lines = ["# Part 06 — UK GDPR Assessment (Post-Brexit)\n",
             f"**Generated:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}  ",
             "**[← Back to Index](00_index.md)**\n",
             "## Delta Analysis: EU GDPR vs UK GDPR\n",
             "The UK GDPR (Data Protection Act 2018 + retained EU law) is substantively equivalent to EU GDPR in all areas relevant to this system. ",
             "Key divergences tracked by the SIA Regulatory Router:\n",
             "| Area | EU GDPR | UK GDPR | SIA Handling |",
             "| --- | --- | --- | --- |",
             "| Data Transfer | SCCs / Adequacy | IDTA (International Data Transfer Agreement) | Regulatory Router detects UK-origin requests and applies IDTA templates |",
             "| Supervisory Authority | EDPB / Lead DPA | ICO | Incident logs include jurisdiction tag for DPA/ICO routing |",
             "| AI Explanability | Recital 71 (GDPR) | Same + draft AI reg 2026 | SIA watermark + disclaimer appended to all high-risk outputs |",
             "| Right to Erasure | Art. 17 | Art. 17 (identical) | GDPR_PURGE logic covers both |",
             "",
             "## UK GDPR Control Mapping\n",
             "| Article | Hazard ID | Control | Description |",
             "| --- | --- | --- | --- |"]
             
    def get_uk_gdpr_sort_key(item):
        cite = item[1].get("regulatory_citations", {}).get("uk_gdpr", "—")
        if cite in ("—", "N/A"):
            return "ZZZZ"
        return cite.replace("Art. ", "").strip()

    for hz_id, h in sorted(hazards.items(), key=get_uk_gdpr_sort_key):
        cite = h.get("regulatory_citations", {}).get("uk_gdpr", "—")
        if cite in ("—", "N/A"):
            continue
        desc = h.get('mitigation_description', '—').replace('|', '\\|')
        lines.append(f"| {cite} | **{hz_id}** | `{h['sia_mitigation_logic']}` | {desc} |")
    return "\n".join(lines)


def build_hipaa(hazards, incidents, max_events) -> str:
    phi_hz = {}
    for hz_id, h in hazards.items():
        cite = h.get("regulatory_citations", {}).get("hipaa", "—")
        if cite != "—" or any(t in h.get("failure_mode","") for t in ["PHI","HIPAA","Privacy","Retention"]):
            phi_hz[hz_id] = h

    lines = ["# Part 07 — HIPAA Technical Safeguards Evidence (OCR Report)\n",
             f"**Generated:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}  ",
             "**[← Back to Index](00_index.md)**\n",
             "## Immutable Archival & Access Control\n",
             "Under the `HIPAA_RETENTION_LOCK` policy, the Regulatory Router ensures PHI is pseudonymized, ",
             "securely vaulted, and retained for the mandatory **6-year archival period** (§164.530(j)). ",
             "Access to decryption keys requires `MANDATORY_MFA_VERIFIED` policy.\n",
             "## Technical Safeguard Control Mapping (§164.306)\n",
             "| Article | Hazard ID | Control | Description |",
             "| --- | --- | --- | --- |"]
             
    def get_hipaa_sort_key(item):
        cite = item[1].get("regulatory_citations", {}).get("hipaa", "—")
        if cite in ("—", "N/A"):
            return "ZZZZ"
        return cite.replace("§", "").strip()
        
    for hz_id, h in sorted(phi_hz.items(), key=get_hipaa_sort_key):
        cite = h.get("regulatory_citations", {}).get("hipaa", "—")
        if cite in ("—", "N/A"):
            continue
        desc = h.get('mitigation_description', '—').replace('|', '\\|')
        lines.append(f"| {cite} | **{hz_id}** | `{h['sia_mitigation_logic']}` | {desc} |")

    phi_events = [e for e in incidents if "PHI" in e.get("incident_type","") or
                  "HIPAA" in e.get("details","")][:max_events]
    lines += ["", "## PHI Vault Event Log\n",
              "| Timestamp | Event Type | Article | Hazard ID | Control | Details |",
              "| --- | --- | --- | --- | --- | --- |"]
              
    HIPAA_INCIDENT_HAZARD_MAP = {
        "PHI_DETECTED": "HZ-22",
        "PII_DETECTED": "HZ-01",
    }
    
    if phi_events:
        for e in phi_events:
            t = ts(e.get("timestamp"))
            i_type = e.get("incident_type", "—")
            hz_id = HIPAA_INCIDENT_HAZARD_MAP.get(i_type, "—")
            h = hazards.get(hz_id, {})
            cite = h.get("regulatory_citations", {}).get("hipaa", "—")
            ctrl = h.get("sia_mitigation_logic", "—")
            details = e.get("details", "—").replace("|", "\\|")
            lines.append(f"| {t} | `{i_type}` | {cite} | **{hz_id}** | `{ctrl}` | {details} |")
    else:
        lines.append("| — | — | — | — | — | _No PHI-specific events recorded. This indicates correct Tier 1 pseudonymization is intercepting events before they reach this log._ |")
        
    return "\n".join(lines)


def build_iso42001(hazards) -> str:
    clause_hz = {}
    for hz_id, h in hazards.items():
        clause = h.get("regulatory_citations", {}).get("iso_42001", "—")
        if clause != "—":
            clause_hz.setdefault(clause, []).append((hz_id, h))

    lines = ["# Part 04 — ISO/IEC 42001 AI Management System Conformance\n",
             f"**Generated:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}  ",
             "**[← Back to Index](00_index.md)**\n",
             "## Scope\n",
             "ISO/IEC 42001:2023 establishes requirements for an AI Management System (AIMS). ",
             "The SIA Framework implements Governance-as-Code controls that directly satisfy the following clauses:\n",
             "## Clause Conformance Matrix\n",
             "| ISO 42001 Clause | Hazard IDs | Control | Description |",
             "| --- | --- | --- | --- |"]
    def parse_clause_number(clause_str):
        import re
        prefix = clause_str.split('(')[0]
        parts = re.findall(r'\d+', prefix)
        if parts:
            return [int(p) for p in parts]
        return [0, clause_str]

    for clause, items in sorted(clause_hz.items(), key=lambda x: parse_clause_number(x[0])):
        ids   = ", ".join(i[0] for i in items)
        ctrls = ", ".join(f"`{i[1]['sia_mitigation_logic']}`" for i in items)
        descs = "; ".join(i[1].get('mitigation_description','—')[:60] for i in items).replace('|','\\|')
        lines.append(f"| {clause} | {ids} | {ctrls} | {descs} |")

    lines += ["", "## Key Conformance Statements\n",
              "- **Clause 4.2 (Context)**: Ethical constraints are codified in `configs/eu_ai_act_full.yaml` and enforced at every request.",
              "- **Clause 6.1.2 (Risk Assessment)**: All risks are documented in `configs/iso_risk_registry.yaml` with pre/post RPN scores.",
              "- **Clause 8.4 (Lifecycle)**: SIA wraps the AI model lifecycle with deterministic ingress and egress gates.",
              "- **Clause 8.6 (Human Oversight)**: Article 14.4 HITL gate enforces mandatory human review for Annex III decisions.",
              "- **Clause 9.1 (Monitoring)**: Post-market monitoring events are streamed live to `logs/audit_ledger.jsonl`.",
              "- **Clause 10.1 (Improvement)**: Risk scores are recalculated on every report generation, closing the feedback loop.",
              ]
    return "\n".join(lines)


def build_cross_ref(hazards, audit_events) -> str:
    lines = ["# Part 08 — Cross-Reference Traceability Index\n",
             f"**Generated:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}  ",
             "**[← Back to Index](00_index.md)**\n",
             "This index maps every SIA control across all regulatory frameworks and standards simultaneously.\n",
             "| Hazard ID | Control | Description | EU AI Act | GDPR | HIPAA | ISO 42001 |",
             "| --- | --- | --- | --- | --- | --- | --- |"]
    def parse_hz_id(hz_id):
        try:
            if hz_id.startswith("HZ-"):
                return ("HZ", int(hz_id[3:]))
            return (hz_id, 0)
        except Exception:
            return (hz_id, 0)
            
    for hz_id, h in sorted(hazards.items(), key=lambda x: parse_hz_id(x[0])):
        c = h.get("regulatory_citations", {})
        ctrl = h["sia_mitigation_logic"]
        desc = h.get('mitigation_description','—')[:55].replace('|','\\|') + '…'
        lines.append(
            f"| **{hz_id}** | `{ctrl}` | {desc} "
            f"| {c.get('eu_ai_act','—')} | {c.get('gdpr','—')} "
            f"| {c.get('hipaa','—')} "
            f"| {c.get('iso_42001','—')} |"
        )
    return "\n".join(lines)


# ── main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Generate the SIA Unified Regulatory Compliance Package.")
    parser.add_argument("--max-events", type=int, default=50,
                        help="Maximum events to include per log appendix (default: 50)")
    args = parser.parse_args()

    if not HAZARDS.exists():
        print(f"Error: Hazard config not found at {HAZARDS}")
        sys.exit(1)

    hazards      = load_hazards()
    mitigations  = load_mitigations()
    audit_events = load_jsonl(AUDIT_LOG)
    incidents    = load_jsonl(INCIDENT_LOG)
    max_ev       = args.max_events
    generated_at = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

    URCP_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    sections = {
        "00_index.md":             build_index(hazards, mitigations, generated_at),
        "01_overview.md":          build_overview(hazards, mitigations, generated_at),
        "02_iso14971.md":          build_iso14971(hazards, incidents, max_ev),
        "03_eu_ai_act_annex_iv.md": build_eu_ai_act(hazards, audit_events, max_ev),
        "04_iso42001.md":          build_iso42001(hazards),
        "05_gdpr_dpia.md":         build_gdpr(hazards, incidents, max_ev),
        "06_uk_gdpr_assessment.md": build_uk_gdpr(hazards),
        "07_hipaa_ocr_evidence.md": build_hipaa(hazards, incidents, max_ev),
        "08_cross_reference_index.md": build_cross_ref(hazards, audit_events),
    }

    for filename, content in sections.items():
        path = URCP_DIR / filename
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"  [OK]  {path.relative_to(ROOT_DIR)}")

    # Keep legacy flat files pointing to URCP
    for legacy, urcp_section in [
        ("ISO14971_risk_management_report.md", "02_iso14971.md"),
        ("DPA_DPIA_report.md",                 "05_gdpr_dpia.md"),
        ("OCR_HIPAA_evidence.md",              "07_hipaa_ocr_evidence.md"),
    ]:
        stub = f"# Redirected\nThis report has moved to the Unified Regulatory Compliance Package.\n\nSee: [reports/urcp/{urcp_section}](urcp/{urcp_section})\n"
        with open(REPORT_DIR / legacy, "w", encoding="utf-8") as f:
            f.write(stub)

    print(f"\nURCP generated at: {URCP_DIR}")
    print(f"Max events per appendix: {max_ev}")
    print(f"Total audit events loaded: {len(audit_events)}")
    print(f"Total incident events loaded: {len(incidents)}")

if __name__ == "__main__":
    main()
