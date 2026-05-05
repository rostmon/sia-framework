# SIA Framework: Risk Management Plan & Report

**Document Version:** 1.1
**Date:** 2026-04-22
**Standard Alignment:** ISO 14971, EU AI Act Article 9

## 1. Risk Management Scope

This document details the risk management activities for the **Sovereign Systemic Integrity Architecture (SIA)**. Because SIA acts as a middleware intended to govern High-Risk LLMs, its risk management focuses heavily on mitigating the hazards introduced by non-deterministic AI models.

## 2. Risk Acceptability Criteria

Risks are evaluated using a standard matrix combining **Severity of Harm** (1-5) and **Probability of Occurrence** (1-5). The Risk Priority Number (RPN) is calculated as `Severity x Probability`.

- **Acceptable (RPN 1-8):** No further mitigation required.
- **ALARP (As Low As Reasonably Practicable) (RPN 9-15):** Mitigation required unless technical limitations prevent it.
- **Unacceptable (RPN 16-25):** Mandatory mitigation required before deployment.

## 3. Comprehensive Hazard Analysis Matrix

The following table outlines the primary AI hazards identified, their unmitigated RPN, the deterministic SIA mitigation applied, and the residual risk.

| Hazard ID | Hazard Description | Consequence | Unmitigated RPN | SIA Technical Mitigation (Governance-as-Code) | Residual RPN |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **HZ-01** | **PII Leakage:** User inputs sensitive medical or financial data into the prompt, which is sent to external LLM. | Data Breach, GDPR violation. | **20** (Sev:4, Prob:5) | **Ingress Sanitizer:** (`article_10_3`) `STRIP_PII` regex dynamically redacts data before network transit. | **4** (Sev:4, Prob:1) |
| **HZ-02** | **Automated High-Risk Decision:** LLM is used to automatically score a resume or diagnose a patient. | Discrimination, Loss of Rights. | **25** (Sev:5, Prob:5) | **HITL Gate:** (`article_14_4`) Keywords matching Annex III trigger `HTTP 202` pausing execution for a human signature. | **5** (Sev:5, Prob:1) |
| **HZ-03** | **Hallucination / Confabulation:** LLM generates a highly fluent but factually incorrect response. | User harm, misdiagnosis. | **16** (Sev:4, Prob:4) | **Truth Razor:** (`article_15_3`) Egress grounding engine requires `MIN_CONFIDENCE: 0.85`. Executes `BLOCK_AND_REWRITE` if failed. | **4** (Sev:4, Prob:1) |
| **HZ-04** | **Automation Bias:** User implicitly trusts LLM output without realizing it is AI-generated. | Overreliance, user error. | **12** (Sev:3, Prob:4) | **Transparency:** (`article_13_1`) Egress engine automatically appends `APPEND_WATERMARK` to all compliant outputs. | **3** (Sev:3, Prob:1) |
| **HZ-05** | **Lack of Traceability:** System generates a harmful output but there is no record of the prompt or reasoning. | Non-compliance, lack of accountability. | **15** (Sev:3, Prob:5) | **Audit Ledger:** (`article_12_1`) Traceability engine hashes all interactions with SHA-256 into `audit_ledger.jsonl`. | **3** (Sev:3, Prob:1) |
## 3. Automated Hazard Analysis & Traceability Matrix

The SIA Framework implements an automated risk management lifecycle. Hazards are centrally defined in `configs/iso_14971_hazards.yaml` and mapped to deterministic governance logic.

### Hazard Identification Matrix
The master Hazard Traceability Matrix is automatically generated based on the current configuration. It includes:
- **Hazard IDs (HZ-01 through HZ-21)**: Mapping failure modes to consequences.
- **Risk Evaluation**: Pre-mitigation and Residual RPN (Severity x Probability).
- **Technical Mitigations**: Direct traceability to `SIA Mitigation Logic` (e.g., `STRIP_PII`, `BLOCK_PROMPT_INJECTION`).
- **Mitigation Descriptions**: Detailed technical rationale for each deterministic gate.

> [!TIP]
> View the latest generated report here: [reports/ISO14971_risk_management_report.md](../reports/ISO14971_risk_management_report.md)

## 4. Post-Market Monitoring (PMM) Traceability

In accordance with **Article 72** of the EU AI Act, SIA maintains a live link between runtime incidents and the Risk Management Matrix. When an incident is detected (e.g., Anomaly Detection, Low Confidence, or Rate Limiting), it is logged and automatically traced back to the corresponding Hazard ID in the ISO 14971 report.

This ensure that risk management is a "live" process, with real-world failure frequencies directly impacting the system's risk profile.

## 5. Conclusion of Risk Acceptability

After the application of the SIA Governance-as-Code mitigations, all identified hazards (including prohibited practices, data governance, and cybersecurity risks) have been reduced to an **Acceptable** residual risk level (RPN ≤ 8). The overall residual risk posed by the LLM when wrapped by the SIA framework is deemed acceptable in relation to its intended benefits.
