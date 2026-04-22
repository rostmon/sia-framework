# EU AI Act: Annex IV Technical Documentation Evidence
**Generated on:** 2026-04-22T09:27:51.895882Z

This report provides objective runtime evidence of compliance with the EU AI Act High-Risk System requirements, generated directly from the immutable `audit_ledger.jsonl`.

## 1. Runtime Operational Summary
- **Total Standard Inferences Processed:** 2
- **Total Active Interventions:** 2
- **Average Compliance Confidence Score:** 0.45

## 2. Article 10 (Data Governance) Evidence
*Requirement: Data sets must be free of errors, personal data safeguarded, and biases examined.*
- **PII Sanitization Events Executed (`STRIP_PII`):** 1 instances where sensitive personal data was automatically redacted.
- **Prohibited Bias Blocks (`BLOCK_PROHIBITED_DOMAINS`):** 1 instances where requests mapping to hate speech/discrimination were rejected.

## 3. Article 14 (Human Oversight) Evidence
*Requirement: High-risk Annex III tasks must allow for human intervention.*
- **Human Veto Gates Triggered (`HTTP 202`):** 1 instances where the system detected high-risk intent (e.g., employment, healthcare) and paused execution for mandatory human signature.

## 4. Article 15 (Accuracy and Robustness) Evidence
*Requirement: System must be resilient against hallucinations and errors.*
- **Hallucinations Blocked (`BLOCK_AND_REWRITE`):** 1 instances where the Truth Razor detected low-confidence/unverified facts and intercepted the output.

## 5. Article 12 (Traceability) Cryptographic Ledger
*Requirement: Automatic recording of events.*
Below is a sampled audit trail of the most recent cryptographic signatures anchoring these events to the immutable ledger:

| Timestamp | SHA-256 Signature Hash |
| :--- | :--- |
| 2026-04-22T09:27:51.823311Z | `3dd8a835d3a50e6f84070623df1b0ca683c874967a0b0cdefda3ce1c8dfea436` |
| 2026-04-22T09:27:51.828385Z | `ab219717c4cc2e315e5dc1bec1849389d4412e65d7ae3f5201cc7e9fd6cb3202` |
| 2026-04-22T09:27:51.833435Z | `d3a198ef4ded5ba9cdd73a916a78b6f45cc38ad8f92f94e9569abffd1f691ca1` |
| 2026-04-22T09:27:51.836256Z | `9088cc606abc56fe73f9ec6eb84c989360a064bc8c7120080f52b96d64603842` |
