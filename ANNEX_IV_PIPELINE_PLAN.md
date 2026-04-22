# Implementation Plan: Annex IV Compliance Reporting Pipeline

To satisfy the EU AI Act's **Annex IV (Technical Documentation)** and **Article 12 (Record-Keeping)** requirements, we need a mechanism to convert raw audit logs into human-readable objective evidence. 

This plan outlines the creation of an automated reporting pipeline that parses the `audit_ledger.jsonl` and generates a structured Markdown artifact. This artifact can be directly appended to your official Technical File for regulatory audits.

## ⚖️ Background Context
The SIA framework is currently logging cryptographic hashes, confidence scores, and reasoning paths for every interaction into an immutable JSONL ledger. While this satisfies raw technical traceability, auditors require aggregated, human-readable evidence of the system's runtime controls in action.

## 🛠️ Proposed Changes

### [NEW] `src/sia/traceability/reporter.py`
We will build a new Python module (`ComplianceReporter`) responsible for:
1.  **Ledger Ingestion:** Reading the `audit_ledger.jsonl`.
2.  **Metric Aggregation:** Calculating average compliance scores, total blocked requests, and total human vetoes.
3.  **Artifact Generation:** Outputting a formatted `ANNEX_IV_EVIDENCE.md` document.

### [Component: The Generated Markdown Artifact]
The generated `ANNEX_IV_EVIDENCE.md` will contain the following sections mapping to the EU AI Act:

1.  **Runtime Operational Summary:** Total inferences processed and average confidence scores.
2.  **Article 10 (Data Governance) Evidence:** Number of PII sanitization events executed at runtime.
3.  **Article 14 (Human Oversight) Evidence:** A log of Annex III high-risk triggers that successfully routed to human review (`HTTP 202`).
4.  **Article 15 (Accuracy/Robustness) Evidence:** Number of hallucinated responses blocked and rewritten by the Truth Razor.
5.  **Article 12 (Traceability) Cryptographic Ledger:** A sampled table of the most recent SHA-256 signatures tying the report to the immutable data.

---

## ✅ Verification Plan

1. **Run the PoC Multiple Times:** We will run `test_poc.py` a few times to populate `audit_ledger.jsonl` with multiple records.
2. **Execute Reporter:** We will run `python -m sia.traceability.reporter`.
3. **Validate Output:** Ensure `ANNEX_IV_EVIDENCE.md` is generated, formatted correctly, and accurately reflects the metrics in the ledger.
