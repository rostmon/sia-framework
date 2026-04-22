# EU AI Act: Annex IV Technical Documentation Evidence
**Generated on:** 2026-04-22T10:17:04.691297Z

This report provides objective runtime evidence of compliance with the EU AI Act High-Risk System requirements, generated directly from the immutable `audit_ledger.jsonl`.

## 1. Runtime Operational Summary
- **Total Standard Inferences Processed:** 5
- **Total Active Interventions:** 11
- **Average Compliance Confidence Score:** 0.57

## 2. Article 5 (Prohibited Practices) Evidence
*Requirement: Ban on unacceptable risk AI practices.*
- **Prohibited Practices Blocked (`BLOCK_PROHIBITED_PRACTICES`):** 0 instances where requests for social scoring or biometric surveillance were intercepted and dropped.

## 3. Article 10 (Data Governance) Evidence
*Requirement: Data sets must be free of errors, personal data safeguarded, and biases examined.*
- **PII Sanitization Events Executed (`STRIP_PII`):** 1 instances where sensitive personal data was automatically redacted.
- **Prohibited Bias Blocks (`BLOCK_PROHIBITED_DOMAINS`):** 1 instances where requests mapping to hate speech/discrimination were rejected.

## 4. Article 13 (Transparency) Evidence
*Requirement: Users must be informed of AI generation and system limitations.*
- **Contextual Disclaimers Appended (`APPEND_DISCLAIMER`):** 0 instances where Annex III specific disclaimers (e.g. Healthcare) were dynamically added to the AI output.

## 5. Article 14 (Human Oversight) Evidence
*Requirement: High-risk Annex III tasks must allow for human intervention.*
- **Human Veto Gates Triggered (`HTTP 202`):** 3 instances where the system detected high-risk intent (e.g., employment, healthcare) and paused execution for mandatory human signature.

## 6. Article 15 (Accuracy, Robustness, and Cybersecurity) Evidence
*Requirement: System must be resilient against hallucinations and adversarial attacks.*
- **Hallucinations Blocked (`BLOCK_AND_REWRITE`):** 2 instances where the Truth Razor detected low-confidence/unverified facts and intercepted the output.
- **Prompt Injections Blocked (`BLOCK_PROMPT_INJECTION`):** 1 instances where adversarial jailbreaks were detected and blocked at ingress.

## 7. Article 12 (Traceability) Cryptographic Ledger
*Requirement: Automatic recording of events.*
Below is a sampled audit trail of the most recent cryptographic signatures anchoring these events to the immutable ledger:

| Timestamp | SHA-256 Signature Hash |
| :--- | :--- |
| 2026-04-22T10:16:46.216295Z | `a3ff02cc8b5ae34f2c35b834b39e895d406a1d5588874972a3054c6e38f9c869` |
| 2026-04-22T10:16:46.228987Z | `8c7dc4849dffa28a7b09d3aaf66fd1b26c8313718d1fc3517aeec32e71b9c91a` |
| 2026-04-22T10:16:46.239562Z | `6ed5a4c8be2c9ef7b387857ee9154c950f343f368251a70f326b6a52b66bd397` |
| 2026-04-22T10:16:46.245006Z | `21e24b73bb635e688f59fe0ae5d4ae387c7130db23baff343338ea7dea2f1832` |
| 2026-04-22T10:16:46.263087Z | `7ed9c948c177bb64ce3810f551536c1cb7bac716e5f8ff8e7a01d6918989075c` |
| 2026-04-22T10:16:46.275816Z | `3915e2ed84dca5c4336ed0ef7b9388942b96d553013be55bac444e5f9e950dd1` |
| 2026-04-22T10:16:46.285670Z | `9fe84512f9ccae7197dd6cb0880d0b71d369fb919d529ff85385b2d3042a4e47` |
