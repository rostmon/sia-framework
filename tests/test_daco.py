import unittest
import shutil
import tempfile
import json
from pathlib import Path

from sia.traceability.daco import DACOKeyRing, BlockchainAnchor
from sia.traceability.ledger import AuditLedger

class TestDACO(unittest.TestCase):
    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp())
        self.pem_path = self.temp_dir / "daco_officer.pem"
        self.blockchain_path = self.temp_dir / "daco_blockchain.jsonl"
        self.ledger_path = self.temp_dir / "audit_ledger.jsonl"

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_key_ring_creation_and_persistence(self):
        # First creation generates key
        ring1 = DACOKeyRing(pem_path=self.pem_path)
        self.assertTrue(self.pem_path.exists())
        self.assertTrue(ring1.did.startswith("did:ethr:"))
        self.assertTrue(ring1.address.startswith("0x"))
        self.assertEqual(len(ring1.address), 42)
        
        # Second creation loads existing key (deterministic identity)
        ring2 = DACOKeyRing(pem_path=self.pem_path)
        self.assertEqual(ring1.did, ring2.did)
        self.assertEqual(ring1.address, ring2.address)

    def test_signature_verification(self):
        ring = DACOKeyRing(pem_path=self.pem_path)
        payload = {"data": "clinical_compliance", "value": 98.5}
        
        sig = ring.sign_payload(payload)
        # Signature is a hex string
        self.assertTrue(len(sig) > 0)
        self.assertTrue(ring.verify_payload(payload, sig))
        
        # Altered payload should fail verification
        payload_altered = {"data": "clinical_compliance", "value": 98.6}
        self.assertFalse(ring.verify_payload(payload_altered, sig))

    def test_merkle_root_calculation(self):
        anchor = BlockchainAnchor(db_path=self.blockchain_path)
        
        # Single hash
        h1 = "a" * 64
        root = anchor.compute_merkle_root([h1])
        self.assertEqual(root, h1)
        
        # Two hashes
        h2 = "b" * 64
        import hashlib
        expected_combined = hashlib.sha256(h1.encode("utf-8") + h2.encode("utf-8")).hexdigest()
        root2 = anchor.compute_merkle_root([h1, h2])
        self.assertEqual(root2, expected_combined)
        
        # Odd number of hashes (should duplicate the last)
        h3 = "c" * 64
        root3_odd = anchor.compute_merkle_root([h1, h2, h3])
        root3_even = anchor.compute_merkle_root([h1, h2, h3, h3])
        self.assertEqual(root3_odd, root3_even)

    def test_blockchain_anchoring_trigger(self):
        # Setup AuditLedger pointing to temp paths
        ledger = AuditLedger(db_path=str(self.ledger_path))
        # Point its sub-modules to our temp paths
        ledger.keyring = DACOKeyRing(pem_path=self.pem_path)
        ledger.anchor = BlockchainAnchor(db_path=self.blockchain_path)
        
        # Record 4 events: shouldn't trigger block 1 yet
        for i in range(4):
            ledger.record_trace(
                prompt=f"prompt {i}",
                sanitized_prompt=f"prompt {i}",
                reasoning_path="none",
                output="output",
                compliance_score=1.0
            )
        self.assertEqual(ledger.anchor.get_latest_block()["block_height"], 0)
        
        # Record 5th event: block 1 should trigger
        ledger.record_trace(
            prompt="prompt 5",
            sanitized_prompt="prompt 5",
            reasoning_path="none",
            output="output",
            compliance_score=1.0
        )
        latest_block = ledger.anchor.get_latest_block()
        self.assertEqual(latest_block["block_height"], 1)
        self.assertEqual(latest_block["tx_count"], 5)
        self.assertTrue(len(latest_block["merkle_root"]) > 0)
        
        # Confirm that the signature hashes match the records
        hashes = []
        with open(self.ledger_path, "r", encoding="utf-8") as f:
            for line in f:
                hashes.append(json.loads(line)["signature_hash"])
        self.assertEqual(latest_block["tx_hashes"], hashes)
        
        # Record 5 more: block 2 should trigger
        for i in range(5):
            ledger.record_intervention(
                prompt=f"intervention {i}",
                trigger_paragraph="Art 5",
                action_taken="BLOCK"
            )
        self.assertEqual(ledger.anchor.get_latest_block()["block_height"], 2)

if __name__ == "__main__":
    unittest.main()
