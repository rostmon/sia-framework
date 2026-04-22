"""SIA Monitoring — metrics collector reading from audit_ledger.jsonl."""
from __future__ import annotations
import json
from collections import defaultdict, Counter
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional


def _parse_ts(ts: str) -> datetime:
    return datetime.fromisoformat(ts.replace("Z", "+00:00")).replace(tzinfo=None)


class MetricsCollector:
    """Reads audit_ledger.jsonl and computes all runtime monitoring metrics."""

    def __init__(self, ledger_path: str = "logs/audit_ledger.jsonl"):
        self.ledger_path = Path(ledger_path)

    def _load_entries(self) -> List[Dict[str, Any]]:
        if not self.ledger_path.exists():
            return []
        entries = []
        with open(self.ledger_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        entries.append(json.loads(line))
                    except json.JSONDecodeError:
                        pass
        return entries

    def compute(self) -> Dict[str, Any]:
        entries = self._load_entries()
        if not entries:
            return self._empty_metrics()

        total = len(entries)
        interventions = [e for e in entries if e.get("type") == "intervention"]
        inferences    = [e for e in entries if e.get("type") == "inference"]

        # ── Action distribution ──────────────────────────────────────────────
        action_counts: Counter = Counter()
        for e in interventions:
            action = e.get("action_taken", "UNKNOWN")
            if "BLOCKED" in action:
                action_counts["BLOCKED"] += 1
            elif "HUMAN_VETO" in action:
                action_counts["HUMAN_VETO"] += 1
        for e in inferences:
            score = e.get("compliance_score", 0)
            if score > 0:
                action_counts["PASSED"] += 1
            else:
                action_counts["REWRITTEN"] += 1

        passed  = action_counts.get("PASSED", 0)
        blocked = action_counts.get("BLOCKED", 0)
        vetoed  = action_counts.get("HUMAN_VETO", 0)
        rewritten = action_counts.get("REWRITTEN", 0)
        compliance_rate = round((passed / total) * 100, 1) if total else 0.0

        # ── Article trigger frequency ────────────────────────────────────────
        article_counts: Counter = Counter()
        for e in interventions:
            para = e.get("trigger_paragraph")
            if para:
                article_counts[para] += 1

        # ── Confidence distribution (inferences only) ────────────────────────
        scores = [e.get("compliance_score", 0.0) for e in inferences]
        avg_confidence = round(sum(scores) / len(scores), 3) if scores else 0.0

        # ── PII redactions ───────────────────────────────────────────────────
        pii_count = sum(1 for e in inferences if e.get("pii_sanitized"))

        # ── Consecutive block detection (Art. 72.1 anomaly) ──────────────────
        max_consecutive = 0
        current_run = 0
        anomaly_alert = False
        for e in entries:
            if e.get("type") == "intervention" and "BLOCKED" in e.get("action_taken", ""):
                current_run += 1
                max_consecutive = max(max_consecutive, current_run)
            else:
                current_run = 0
        if max_consecutive >= 5:
            anomaly_alert = True

        # ── Time-series bucketing (last 60 min, 5-min buckets) ───────────────
        now = datetime.utcnow()
        buckets: Dict[str, Dict[str, int]] = {}
        for i in range(12):
            bucket_start = now - timedelta(minutes=(11 - i) * 5)
            label = bucket_start.strftime("%H:%M")
            buckets[label] = {"passed": 0, "blocked": 0, "vetoed": 0, "rewritten": 0}

        for e in entries:
            try:
                ts = _parse_ts(e["timestamp"])
                age_mins = (now - ts).total_seconds() / 60
                if age_mins > 60:
                    continue
                bucket_idx = int(age_mins / 5)
                bucket_idx = min(bucket_idx, 11)
                bucket_start = now - timedelta(minutes=(11 - (11 - bucket_idx)) * 5)
                label = (now - timedelta(minutes=bucket_idx * 5)).strftime("%H:%M")
                # find closest bucket label
                closest = min(buckets.keys(),
                    key=lambda k: abs((datetime.strptime(k, "%H:%M").replace(
                        year=now.year, month=now.month, day=now.day) - ts).total_seconds()))
                action = e.get("action_taken", "")
                score  = e.get("compliance_score", 0.0)
                if e.get("type") == "intervention":
                    if "BLOCKED" in action:
                        buckets[closest]["blocked"] += 1
                    elif "VETO" in action:
                        buckets[closest]["vetoed"] += 1
                else:
                    if score > 0:
                        buckets[closest]["passed"] += 1
                    else:
                        buckets[closest]["rewritten"] += 1
            except Exception:
                pass

        # ── Recent events (last 10) ───────────────────────────────────────────
        recent = []
        for e in reversed(entries[-10:]):
            recent.append({
                "timestamp": e.get("timestamp", ""),
                "type": e.get("type", ""),
                "action": e.get("action_taken", "PASSED" if e.get("compliance_score", 0) > 0 else "REWRITTEN"),
                "article": e.get("trigger_paragraph", "—"),
                "prompt_preview": (e.get("prompt", "")[:60] + "...") if len(e.get("prompt", "")) > 60 else e.get("prompt", ""),
                "hash": e.get("signature_hash", "")[:16],
            })
        recent.reverse()

        return {
            "summary": {
                "total_requests": total,
                "passed": passed,
                "blocked": blocked,
                "human_veto": vetoed,
                "rewritten": rewritten,
                "compliance_rate": compliance_rate,
                "avg_confidence": avg_confidence,
                "pii_redactions": pii_count,
                "anomaly_alert": anomaly_alert,
                "max_consecutive_blocks": max_consecutive,
            },
            "article_triggers": dict(article_counts.most_common(10)),
            "action_distribution": dict(action_counts),
            "timeseries": {
                "labels": list(buckets.keys()),
                "passed": [v["passed"] for v in buckets.values()],
                "blocked": [v["blocked"] for v in buckets.values()],
                "vetoed": [v["vetoed"] for v in buckets.values()],
                "rewritten": [v["rewritten"] for v in buckets.values()],
            },
            "recent_events": recent,
            "generated_at": datetime.utcnow().isoformat() + "Z",
        }

    def _empty_metrics(self) -> Dict[str, Any]:
        empty_ts = {"labels": [], "passed": [], "blocked": [], "vetoed": [], "rewritten": []}
        return {
            "summary": {
                "total_requests": 0, "passed": 0, "blocked": 0, "human_veto": 0,
                "rewritten": 0, "compliance_rate": 0.0, "avg_confidence": 0.0,
                "pii_redactions": 0, "anomaly_alert": False, "max_consecutive_blocks": 0,
            },
            "article_triggers": {},
            "action_distribution": {},
            "timeseries": empty_ts,
            "recent_events": [],
            "generated_at": datetime.utcnow().isoformat() + "Z",
        }
