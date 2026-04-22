import hashlib
import json
from datetime import datetime
from typing import Any, Dict, Optional

class AuditLedger:
    def __init__(self, db_path: str = "logs/audit_ledger.jsonl"):
        self.db_path = db_path

    def _hash_payload(self, payload: Dict[str, Any]) -> str:
        payload_str = json.dumps(payload, sort_keys=True)
        return hashlib.sha256(payload_str.encode('utf-8')).hexdigest()

    def record_trace(self, prompt: str, sanitized_prompt: str, reasoning_path: str, output: str, compliance_score: float) -> str:
        record = {
            "type": "inference",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "prompt": prompt,
            "sanitized_prompt": sanitized_prompt,
            "reasoning_path": reasoning_path,
            "output": output,
            "compliance_score": compliance_score,
            "pii_sanitized": prompt != sanitized_prompt
        }
        record_hash = self._hash_payload(record)
        record["signature_hash"] = record_hash
        
        with open(self.db_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")
            
        return record_hash

    def record_intervention(self, prompt: str, trigger_paragraph: str, action_taken: str) -> str:
        """Logs a pre-emptive action like a Human Veto."""
        record = {
            "type": "intervention",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "prompt": prompt,
            "trigger_paragraph": trigger_paragraph,
            "action_taken": action_taken
        }
        record_hash = self._hash_payload(record)
        record["signature_hash"] = record_hash
        
        with open(self.db_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")
            
        return record_hash
