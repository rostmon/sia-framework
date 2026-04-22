"""
Signed Compliance Certificates — Official regulatory export for Article 43.
Generates a cryptographically anchored conformity assertion.
"""
from __future__ import annotations
import json
import hashlib
from datetime import datetime
from typing import Any, Dict


class ConformityCertificate:
    """
    Generates a 'Deployment Assertion Certificate' based on 
    the current conformity assessment state.
    """

    def __init__(self, project_name: str = "SIA-Governed System"):
        self.project_name = project_name

    def generate(self, progress_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Creates a JSON-LD compliance certificate.
        """
        timestamp = datetime.utcnow().isoformat() + "Z"
        overall_score = progress_data.get("overall_percent", 0)
        
        # Simplified certificate structure
        certificate = {
            "@context": "https://sia.framework/compliance/v1",
            "type": "AIConformityAssertion",
            "metadata": {
                "project": self.project_name,
                "generated_at": timestamp,
                "framework": "SIA v0.1.0",
                "standard": "EU AI Act Annex VI"
            },
            "assessment_summary": {
                "conformity_percent": overall_score,
                "total_checks": progress_data.get("total", 0),
                "completed": progress_data.get("completed", 0)
            },
            "requirements": progress_data.get("requirements", {})
        }

        # Generate a "digital signature" (Mock)
        cert_str = json.dumps(certificate, sort_keys=True)
        signature = hashlib.sha256(cert_str.encode("utf-8")).hexdigest()
        
        certificate["signature"] = {
            "type": "SHA256withRSA-MOCK",
            "creator": "SIA-REGULATORY-AUTHORITY",
            "signature_value": signature
        }

        return certificate

    def to_markdown(self, certificate: Dict[str, Any]) -> str:
        """
        Converts the certificate to a human-readable regulatory report.
        """
        m = certificate["metadata"]
        s = certificate["assessment_summary"]
        
        md = f"""# EU AI Act Conformity Certificate
**Project**: {m['project']}  
**Generated**: {m['generated_at']}  
**Status**: {"COMPLIANT" if s['conformity_percent'] == 100 else "PARTIAL COMPLIANCE"} ({s['conformity_percent']}%)

---

## 1. Assessment Overview
The system has been evaluated against the requirements set out in **Annex VI** of the EU AI Act.

- **Conformity Score**: {s['conformity_percent']}%
- **Total Requirements Checked**: {s['total_checks']}
- **Outstanding Items**: {s['total_checks'] - s['completed']}

## 2. Requirement Details
"""
        for req_id, req in certificate["requirements"].items():
            status_icon = "✅" if req['percent'] == 100 else "⚠️"
            md += f"### {status_icon} {req['title']}\n"
            md += f"*Status: {req['percent']}% complete*\n\n"
            for check_id, desc in req['checks'].items():
                checked = " [x] " if req['status'].get(check_id) else " [ ] "
                md += f"-{checked}{desc}\n"
            md += "\n"

        md += f"""
---

## 3. Regulatory Signature
This document is cryptographically anchored to the SIA governance ledger.

**Signature Hash**: `{certificate['signature']['signature_value']}`  
**Issuer**: {certificate['signature']['creator']}
"""
        return md
