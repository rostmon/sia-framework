# EU AI Act: Annex IV Technical Documentation Evidence
**Generated on:** 2026-04-22T09:33:46.612976Z

This report provides objective runtime evidence of compliance with the EU AI Act High-Risk System requirements, generated directly from the immutable `audit_ledger.jsonl`.

## 1. Runtime Operational Summary
- **Total Standard Inferences Processed:** 3
- **Total Active Interventions:** 5
- **Average Compliance Confidence Score:** 0.60

## 2. Article 5 (Prohibited Practices) Evidence
*Requirement: Ban on unacceptable risk AI practices.*
- **Prohibited Practices Blocked (`BLOCK_PROHIBITED_PRACTICES`):** 1 instances where requests for social scoring or biometric surveillance were intercepted and dropped.

## 3. Article 10 (Data Governance) Evidence
*Requirement: Data sets must be free of errors, personal data safeguarded, and biases examined.*
- **PII Sanitization Events Executed (`STRIP_PII`):** 1 instances where sensitive personal data was automatically redacted.
- **Prohibited Bias Blocks (`BLOCK_PROHIBITED_DOMAINS`):** 1 instances where requests mapping to hate speech/discrimination were rejected.

## 4. Article 13 (Transparency) Evidence
*Requirement: Users must be informed of AI generation and system limitations.*
- **Contextual Disclaimers Appended (`APPEND_DISCLAIMER`):** 1 instances where Annex III specific disclaimers (e.g. Healthcare) were dynamically added to the AI output.

## 5. Article 14 (Human Oversight) Evidence
*Requirement: High-risk Annex III tasks must allow for human intervention.*
- **Human Veto Gates Triggered (`HTTP 202`):** 1 instances where the system detected high-risk intent (e.g., employment, healthcare) and paused execution for mandatory human signature.

## 6. Article 15 (Accuracy, Robustness, and Cybersecurity) Evidence
*Requirement: System must be resilient against hallucinations and adversarial attacks.*
- **Hallucinations Blocked (`BLOCK_AND_REWRITE`):** 1 instances where the Truth Razor detected low-confidence/unverified facts and intercepted the output.
- **Prompt Injections Blocked (`BLOCK_PROMPT_INJECTION`):** 1 instances where adversarial jailbreaks were detected and blocked at ingress.

## 7. Article 12 (Traceability) Cryptographic Ledger
*Requirement: Automatic recording of events.*
Below is a sampled audit trail of the most recent cryptographic signatures anchoring these events to the immutable ledger:

| Timestamp | SHA-256 Signature Hash |
| :--- | :--- |
| 2026-04-22T09:33:46.530835Z | `7fdaf444db29945ad6736f1eb4e02b373c36b7404c2c9019526827e6686831b0` |
| 2026-04-22T09:33:46.535540Z | `a01109261a4927b70e70d3e86bfaa46f1dcfe3e7fa80fb4569d118695c1f629c` |
| 2026-04-22T09:33:46.540950Z | `a330830fbf261c68d1bb83a55536f7042a0f3af51d3edbf5e8b937f1c68ede35` |
| 2026-04-22T09:33:46.543673Z | `c7ad87067526774c901f562dc61ea7a1df489d5117525438502da7bf72de1e8c` |
| 2026-04-22T09:33:46.548952Z | `2c164f1b96ee2c6f4805d4b716b9d0a2842f86303dc254b3b9d811dd2c5945ec` |
| 2026-04-22T09:33:46.550025Z | `0be1b3e5d967fd6451de48f7d98c42b03ca7b3f10343cc5130d4ce3ffbdb3c79` |
| 2026-04-22T09:33:46.550025Z | `667d3e7f559ca5c42cf557ea852a1a83cf1d4ce3937144bcbe44dc6cbc9c7488` |
