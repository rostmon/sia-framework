import os
import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, List

from sia.traceability.daco import DACOKeyRing, BlockchainAnchor

class AuditLedger:
    def __init__(self, db_path: str = "logs/audit_ledger.jsonl"):
        self.db_path = db_path
        self.keyring = DACOKeyRing()
        self.anchor = BlockchainAnchor()

    def _hash_payload(self, payload: Dict[str, Any]) -> str:
        payload_str = json.dumps(payload, sort_keys=True)
        return hashlib.sha256(payload_str.encode('utf-8')).hexdigest()

    def _check_blockchain_anchor(self) -> Optional[Dict[str, Any]]:
        """Reads ledger entries, calculates Merkle Roots, and anchors states every 5 entries."""
        hashes: List[str] = []
        if os.path.exists(self.db_path):
            with open(self.db_path, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        try:
                            data = json.loads(line)
                            sig = data.get("signature_hash")
                            if sig:
                                hashes.append(sig)
                        except:
                            pass
        
        if not hashes:
            return None
            
        latest_block = self.anchor.get_latest_block()
        expected_blocks = len(hashes) // 5
        if expected_blocks > latest_block["block_height"]:
            # Anchor hashes up to the latest multiple of 5
            subset_hashes = hashes[:expected_blocks * 5]
            return self.anchor.anchor_state(subset_hashes)
        return None

    def record_trace(self, prompt: str, sanitized_prompt: str, reasoning_path: str, output: str, compliance_score: float, privacy_manifest: Optional[Dict[str, Any]] = None) -> str:
        record = {
            "type": "inference",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "prompt": prompt,
            "sanitized_prompt": sanitized_prompt,
            "reasoning_path": reasoning_path,
            "output": output,
            "compliance_score": compliance_score,
            "pii_sanitized": prompt != sanitized_prompt,
            "privacy_manifest": privacy_manifest
        }
        record_hash = self._hash_payload(record)
        record["signature_hash"] = record_hash
        
        # Sign with DACO key ring
        record["daco_did"] = self.keyring.did
        record["daco_signature"] = self.keyring.sign_payload(record)
        
        with open(self.db_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")
            
        self._check_blockchain_anchor()
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
        
        # Sign with DACO key ring
        record["daco_did"] = self.keyring.did
        record["daco_signature"] = self.keyring.sign_payload(record)
        
        with open(self.db_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")
            
        self._check_blockchain_anchor()
        return record_hash
