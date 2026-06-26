import os
import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional

from ecdsa import SigningKey, VerifyingKey, SECP256k1, BadSignatureError

_ROOT = Path(__file__).resolve().parent.parent.parent.parent
PEM_PATH = _ROOT / "logs" / "daco_officer.pem"
BLOCKCHAIN_PATH = _ROOT / "logs" / "daco_blockchain.jsonl"

class DACOKeyRing:
    """Manages the decentralized identity (DID) and ECDSA secp256k1 keys of the Compliance Officer."""
    def __init__(self, pem_path: Path = PEM_PATH):
        self.pem_path = pem_path
        self.signing_key = self._load_or_create_key()
        self.verifying_key = self.signing_key.verifying_key
        
        # did:ethr:<ethereum-style-address>
        # Derived from sha256 hash of the uncompressed public key bytes
        public_bytes = self.verifying_key.to_string("uncompressed")
        address_hash = hashlib.sha256(public_bytes).hexdigest()
        self.address = "0x" + address_hash[-40:]
        self.did = f"did:ethr:{self.address}"

    def _load_or_create_key(self) -> SigningKey:
        self.pem_path.parent.mkdir(parents=True, exist_ok=True)
        if self.pem_path.exists():
            with open(self.pem_path, "r", encoding="utf-8") as f:
                return SigningKey.from_pem(f.read())
        else:
            # Generate a new secp256k1 key (EVM compatible)
            sk = SigningKey.generate(curve=SECP256k1)
            with open(self.pem_path, "w", encoding="utf-8") as f:
                f.write(sk.to_pem().decode("utf-8"))
            return sk

    def sign_payload(self, payload: Dict[str, Any]) -> str:
        """Signs a payload dictionary using ECDSA secp256k1, producing a standard hex signature."""
        serialized = json.dumps(payload, sort_keys=True).encode("utf-8")
        signature_bytes = self.signing_key.sign(serialized)
        return signature_bytes.hex()

    def verify_payload(self, payload: Dict[str, Any], signature_hex: str) -> bool:
        """Verifies if the ECDSA signature matches the signed payload."""
        try:
            serialized = json.dumps(payload, sort_keys=True).encode("utf-8")
            sig_bytes = bytes.fromhex(signature_hex)
            return self.verifying_key.verify(sig_bytes, serialized)
        except (BadSignatureError, ValueError, TypeError):
            return False


class BlockchainAnchor:
    """Simulates a Layer 2 rollup blockchain anchor for immutably recording state roots."""
    def __init__(self, db_path: Path = BLOCKCHAIN_PATH):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

    def compute_merkle_root(self, hashes: List[str]) -> str:
        """Computes the Merkle Root of a list of transaction hashes."""
        if not hashes:
            return hashlib.sha256(b"genesis").hexdigest()
        
        current_level = [h.encode("utf-8") if isinstance(h, str) else h for h in hashes]
        
        while len(current_level) > 1:
            next_level = []
            for i in range(0, len(current_level), 2):
                h1 = current_level[i]
                h2 = current_level[i+1] if i + 1 < len(current_level) else h1
                combined = hashlib.sha256(h1 + h2).hexdigest().encode("utf-8")
                next_level.append(combined)
            current_level = next_level
            
        return current_level[0].decode("utf-8") if isinstance(current_level[0], bytes) else current_level[0]

    def get_latest_block(self) -> Dict[str, Any]:
        """Reads the blockchain file and returns the latest block, or genesis info if empty."""
        if not self.db_path.exists():
            return {"block_height": 0, "merkle_root": "0" * 64, "block_hash": "0" * 64}
        
        last_block = None
        with open(self.db_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    try:
                        last_block = json.loads(line)
                    except json.JSONDecodeError:
                        pass
        return last_block or {"block_height": 0, "merkle_root": "0" * 64, "block_hash": "0" * 64}

    def anchor_state(self, tx_hashes: List[str]) -> Dict[str, Any]:
        """Calculates the Merkle Root of the state and commits a new block to the chain."""
        latest = self.get_latest_block()
        new_height = latest["block_height"] + 1
        previous_root = latest.get("merkle_root", "0" * 64)
        
        merkle_root = self.compute_merkle_root(tx_hashes)
        
        block = {
            "block_height": new_height,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "merkle_root": merkle_root,
            "previous_root": previous_root,
            "tx_count": len(tx_hashes),
            "tx_hashes": tx_hashes
        }
        
        # Calculate unique block hash
        block_str = json.dumps(block, sort_keys=True).encode("utf-8")
        block["block_hash"] = hashlib.sha256(block_str).hexdigest()
        
        with open(self.db_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(block) + "\n")
            
        return block
