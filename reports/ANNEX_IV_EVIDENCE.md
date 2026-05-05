# EU AI Act: Annex IV Technical Documentation Evidence
**Generated on:** 2026-05-05T11:45:24.793463Z

This report provides objective runtime evidence of compliance with the EU AI Act High-Risk System requirements, generated directly from the immutable `audit_ledger.jsonl`.

## 1. Runtime Operational Summary
- **Total Standard Inferences Processed:** 177
- **Total Active Interventions:** 87
- **Average Compliance Confidence Score:** 0.28

## 2. Article 5 (Prohibited Practices) Evidence
*Requirement: Ban on unacceptable risk AI practices.*
- **Prohibited Practices Blocked (`BLOCK_PROHIBITED_PRACTICES`):** 0 instances where requests for social scoring or biometric surveillance were intercepted and dropped.

## 3. Article 10 (Data Governance) Evidence
*Requirement: Data sets must be free of errors, personal data safeguarded, and biases examined.*
- **PII Sanitization Events Executed (`STRIP_PII`):** 10 instances where sensitive personal data was automatically redacted.
- **Prohibited Bias Blocks (`BLOCK_PROHIBITED_DOMAINS`):** 6 instances where requests mapping to hate speech/discrimination were rejected.

## 4. Article 13 (Transparency) Evidence
*Requirement: Users must be informed of AI generation and system limitations.*
- **Contextual Disclaimers Appended (`APPEND_DISCLAIMER`):** 0 instances where Annex III specific disclaimers (e.g. Healthcare) were dynamically added to the AI output.

## 5. Article 14 (Human Oversight) Evidence
*Requirement: High-risk Annex III tasks must allow for human intervention.*
- **Human Veto Gates Triggered (`HTTP 202`):** 32 instances where the system detected high-risk intent (e.g., employment, healthcare) and paused execution for mandatory human signature.

## 6. Article 15 (Accuracy, Robustness, and Cybersecurity) Evidence
*Requirement: System must be resilient against hallucinations and adversarial attacks.*
- **Hallucinations Blocked (`BLOCK_AND_REWRITE`):** 123 instances where the Truth Razor detected low-confidence/unverified facts and intercepted the output.
- **Prompt Injections Blocked (`BLOCK_PROMPT_INJECTION`):** 10 instances where adversarial jailbreaks were detected and blocked at ingress.

## 7. Article 12 (Traceability) Cryptographic Ledger
*Requirement: Automatic recording of events.*
Below is a sampled audit trail of the most recent cryptographic signatures anchoring these events to the immutable ledger:

| Timestamp | SHA-256 Signature Hash |
| :--- | :--- |
| 2026-05-05T10:31:47.115788Z | `f5a8d1ebde13e883dec3dc3f05d14824abf845879a2cba2c3112a283bfa0564c` |
| 2026-05-05T10:31:47.116926Z | `c37430eea5c97d36b90a2611e6a21c4bf9249a713198e4df5e750b82284d3932` |
| 2026-05-05T10:31:47.116926Z | `c37430eea5c97d36b90a2611e6a21c4bf9249a713198e4df5e750b82284d3932` |
| 2026-05-05T10:31:47.117432Z | `5cdf88b0e3637f5dcb7b3988c698b08428660460a2441896d29f64a2569cf501` |
| 2026-05-05T10:31:47.117432Z | `5cdf88b0e3637f5dcb7b3988c698b08428660460a2441896d29f64a2569cf501` |
| 2026-05-05T10:31:47.143482Z | `68e7fa5e6d2cd5d6912e3bd75baebec0093e8f6d6cf0e1219ae8157f2240bd8a` |
| 2026-05-05T10:31:47.143482Z | `4d294b0ec1d20a91784eb3abbba81145d6df790496399cf826f79ec62e60e43d` |
