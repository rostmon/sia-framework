# EU AI Act: Annex IV Technical Documentation Evidence
**Generated on:** 2026-04-22T09:03:26.499180Z

This report provides objective runtime evidence of compliance with the EU AI Act High-Risk System requirements, generated directly from the immutable `audit_ledger.jsonl`.

## 1. Runtime Operational Summary
- **Total Standard Inferences Processed:** 2
- **Total Active Interventions:** 1
- **Average Compliance Confidence Score:** 0.45

## 2. Article 10 (Data Governance) Evidence
*Requirement: Data sets must be free of errors and personal data must be safeguarded.*
- **PII Sanitization Events Executed (`STRIP_PII`):** 1 instances where sensitive personal data was automatically redacted prior to LLM processing.

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
| 2026-04-22T09:03:26.431506Z | `66e5725ad1cb4fe395fe86051f20e6a863fd3b5cc0cd356df79bfc6cafb6b5e3` |
| 2026-04-22T09:03:26.437645Z | `2ec303db6b5f62db686d2a21e4b3e79804f9e7e5510cdc87fbe070ead73bba22` |
| 2026-04-22T09:03:26.439654Z | `c4193d13cde6b157ef5e85127cecbe0e4a6cb9bbb452844446299e6065013e95` |
