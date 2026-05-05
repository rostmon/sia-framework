import time
import json
import os
import re
from typing import Dict, Any, Tuple, List
from pathlib import Path
from collections import defaultdict

_ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent
_LOG_DIR = _ROOT_DIR / "logs"
_KILL_SWITCH_FILE = _LOG_DIR / "kill_switch.flag"
_INCIDENT_LOG_FILE = _LOG_DIR / "incident_ledger.jsonl"


class IncidentLogger:
    @staticmethod
    def log_incident(incident_type: str, details: str, input_snapshot: str = None) -> None:
        """Logs an automated incident detection (Article 72 PMM)"""
        if not _LOG_DIR.exists():
            _LOG_DIR.mkdir(parents=True, exist_ok=True)
            
        entry = {
            "timestamp": time.time(),
            "incident_type": incident_type,
            "details": details,
            "input_snapshot": input_snapshot[:500] if input_snapshot else None # Keep it bounded
        }
        with open(_INCIDENT_LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")


class RuntimeRiskManager:
    """
    Manages Runtime Risk Controls for EU AI Act compliance (Articles 9 & 72).
    """
    def __init__(self):
        # In-memory State Storage
        self._request_timestamps = defaultdict(list)
        self._input_length_history = []
        
        # Rate Limiting configuration
        self.rate_limit_window_sec = 60
        self.max_requests_per_window = 50
        
        # Global API Kill Switch State
        self.api_kill_switch_active = False

    def is_kill_switch_active(self) -> bool:
        """
        Checks both the API state and the file-based flag for the emergency kill-switch.
        """
        if self.api_kill_switch_active:
            return True
        if _KILL_SWITCH_FILE.exists():
            return True
        return False

    def set_kill_switch(self, active: bool):
        """Sets the kill-switch state (API logic)."""
        self.api_kill_switch_active = active

    def check_rate_limit(self, client_id: str = "default") -> bool:
        """
        In-memory token bucket rate limiting to prevent Model Inversion / extraction.
        Returns True if allowed, False if blocked.
        """
        current_time = time.time()
        # Clean up old timestamps
        self._request_timestamps[client_id] = [
            t for t in self._request_timestamps[client_id] 
            if current_time - t < self.rate_limit_window_sec
        ]
        
        if len(self._request_timestamps[client_id]) >= self.max_requests_per_window:
            IncidentLogger.log_incident("RATE_LIMIT_EXCEEDED", f"Client {client_id} exceeded limits")
            return False
            
        self._request_timestamps[client_id].append(current_time)
        return True

    def sanitize_input(self, prompt: str) -> str:
        """
        Input Sanitization ("WAF for AI") using Regex.
        Strips high-frequency noise or suspicious perturbations (e.g., invisible characters, massive repetition).
        """
        # Remove zero-width spaces and other non-printable characters
        sanitized = re.sub(r'[\u200b-\u200d\ufeff]', '', prompt)
        
        # Collapse massive repeating special characters (e.g., "!!!!!..." to "!!!")
        sanitized = re.sub(r'([!@#$%^&*()_+={}\[\]:;"\'<>,.?/\\|`~])\1{5,}', r'\1\1\1', sanitized)
        
        return sanitized

    def check_anomaly(self, prompt: str) -> Tuple[bool, str]:
        """
        Checks for anomalies / Data Poisoning on incoming inference.
        Returns (is_anomaly, reason).
        """
        if len(prompt) > 10000:
            reason = "Input exceeds maximum heuristic bounds for anomaly detection"
            IncidentLogger.log_incident("ANOMALY_DETECTED", reason, prompt)
            return True, reason
            
        # Check for excessive unprintable or obscure unicode block density as a simple heuristic
        if len(prompt) > 50:
            ascii_chars = sum(1 for c in prompt if ord(c) < 128)
            if ascii_chars / len(prompt) < 0.1: # Less than 10% standard ascii
                reason = "High density of non-standard characters detected"
                IncidentLogger.log_incident("ANOMALY_DETECTED", reason, prompt)
                return True, reason

        return False, ""

    def update_and_check_drift(self, prompt: str) -> bool:
        """
        Tracks data drift by monitoring input length distribution.
        Returns True if drift is detected.
        """
        current_len = len(prompt)
        self._input_length_history.append(current_len)
        
        # Keep window bounded
        if len(self._input_length_history) > 1000:
            self._input_length_history.pop(0)
            
        if len(self._input_length_history) < 50:
            return False # Not enough data to establish baseline
            
        # Simple heuristic drift: if current input length is 10x the median of the last 50
        recent = sorted(self._input_length_history[-50:])
        median_len = recent[25]
        
        if current_len > (median_len * 10) and current_len > 100:
            IncidentLogger.log_incident("DATA_DRIFT", f"Input length {current_len} deviates from median {median_len}", prompt)
            return True
            
        return False
