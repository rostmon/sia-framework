import json
import os
from datetime import datetime

class ComplianceReporter:
    def __init__(self, ledger_path: str = "audit_ledger.jsonl"):
        self.ledger_path = ledger_path

    def generate_report(self, output_path: str = "ANNEX_IV_EVIDENCE.md"):
        if not os.path.exists(self.ledger_path):
            print(f"Ledger file not found: {self.ledger_path}")
            return

        total_inferences = 0
        total_interventions = 0
        pii_sanitized_count = 0
        article_10_bias_blocks = 0
        article_14_triggers = 0
        article_15_blocks = 0
        article_5_blocks = 0
        article_15_4_blocks = 0
        article_13_disclaimers = 0
        total_confidence = 0.0
        hashes = []

        with open(self.ledger_path, "r", encoding="utf-8") as f:
            for line in f:
                record = json.loads(line)
                hashes.append((record["timestamp"], record["signature_hash"]))
                
                if record["type"] == "inference":
                    total_inferences += 1
                    total_confidence += record.get("compliance_score", 0.0)
                    if record.get("pii_sanitized"):
                        pii_sanitized_count += 1
                    if "[SIA BLOCK]" in record.get("output", ""):
                        article_15_blocks += 1
                    if "Disclaimer:" in record.get("output", ""):
                        article_13_disclaimers += 1
                        
                elif record["type"] == "intervention":
                    total_interventions += 1
                    tp = record.get("trigger_paragraph")
                    if tp == "article_14_4" and record.get("action_taken") == "HTTP_202_ACCEPTED_HUMAN_VETO":
                        article_14_triggers += 1
                    elif tp == "article_10_2_f":
                        article_10_bias_blocks += 1
                    elif tp == "article_5_1":
                        article_5_blocks += 1
                    elif tp == "article_15_4":
                        article_15_4_blocks += 1

        avg_confidence = total_confidence / total_inferences if total_inferences > 0 else 0.0

        md_content = f"""# EU AI Act: Annex IV Technical Documentation Evidence
**Generated on:** {datetime.utcnow().isoformat() + "Z"}

This report provides objective runtime evidence of compliance with the EU AI Act High-Risk System requirements, generated directly from the immutable `audit_ledger.jsonl`.

## 1. Runtime Operational Summary
- **Total Standard Inferences Processed:** {total_inferences}
- **Total Active Interventions:** {total_interventions}
- **Average Compliance Confidence Score:** {avg_confidence:.2f}

## 2. Article 5 (Prohibited Practices) Evidence
*Requirement: Ban on unacceptable risk AI practices.*
- **Prohibited Practices Blocked (`BLOCK_PROHIBITED_PRACTICES`):** {article_5_blocks} instances where requests for social scoring or biometric surveillance were intercepted and dropped.

## 3. Article 10 (Data Governance) Evidence
*Requirement: Data sets must be free of errors, personal data safeguarded, and biases examined.*
- **PII Sanitization Events Executed (`STRIP_PII`):** {pii_sanitized_count} instances where sensitive personal data was automatically redacted.
- **Prohibited Bias Blocks (`BLOCK_PROHIBITED_DOMAINS`):** {article_10_bias_blocks} instances where requests mapping to hate speech/discrimination were rejected.

## 4. Article 13 (Transparency) Evidence
*Requirement: Users must be informed of AI generation and system limitations.*
- **Contextual Disclaimers Appended (`APPEND_DISCLAIMER`):** {article_13_disclaimers} instances where Annex III specific disclaimers (e.g. Healthcare) were dynamically added to the AI output.

## 5. Article 14 (Human Oversight) Evidence
*Requirement: High-risk Annex III tasks must allow for human intervention.*
- **Human Veto Gates Triggered (`HTTP 202`):** {article_14_triggers} instances where the system detected high-risk intent (e.g., employment, healthcare) and paused execution for mandatory human signature.

## 6. Article 15 (Accuracy, Robustness, and Cybersecurity) Evidence
*Requirement: System must be resilient against hallucinations and adversarial attacks.*
- **Hallucinations Blocked (`BLOCK_AND_REWRITE`):** {article_15_blocks} instances where the Truth Razor detected low-confidence/unverified facts and intercepted the output.
- **Prompt Injections Blocked (`BLOCK_PROMPT_INJECTION`):** {article_15_4_blocks} instances where adversarial jailbreaks were detected and blocked at ingress.

## 7. Article 12 (Traceability) Cryptographic Ledger
*Requirement: Automatic recording of events.*
Below is a sampled audit trail of the most recent cryptographic signatures anchoring these events to the immutable ledger:

| Timestamp | SHA-256 Signature Hash |
| :--- | :--- |
"""
        for ts, hsh in hashes[-7:]:  # Show last 7
            md_content += f"| {ts} | `{hsh}` |\n"

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(md_content)
        
        print(f"Compliance report successfully generated at: {output_path}")

if __name__ == "__main__":
    reporter = ComplianceReporter()
    reporter.generate_report()
