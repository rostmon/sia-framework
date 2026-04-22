import hashlib
import json
from datetime import datetime
from typing import Any, Dict

class AuditLedger:
    """
    Immutable ledger for technical file generation and regulatory audits.
    """
    def __init__(self, db_path: str = "audit_ledger.jsonl"):
        # For PoC, we append to a local JSONL file. 
        # In production, this would be a secure append-only DB (e.g., QLDB or PostgreSQL).
        self.db_path = db_path

    def _hash_payload(self, payload: Dict[str, Any]) -> str:
        """
        Generates a SHA-256 hash of the payload for cryptographic anchoring.
        """
        payload_str = json.dumps(payload, sort_keys=True)
        return hashlib.sha256(payload_str.encode('utf-8')).hexdigest()

    def record_trace(self, prompt: str, sanitized_prompt: str, reasoning_path: str, output: str, compliance_score: float) -> str:
        """
        Cryptographically anchors the entire trace.
        """
        record = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "prompt": prompt,
            "sanitized_prompt": sanitized_prompt,
            "reasoning_path": reasoning_path,
            "output": output,
            "compliance_score": compliance_score
        }
        
        record_hash = self._hash_payload(record)
        record["signature_hash"] = record_hash
        
        with open(self.db_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")
            
        return record_hash
