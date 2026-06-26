# Part 08 — Cross-Reference Traceability Index

**Generated:** 2026-06-26 08:45 UTC  
**[← Back to Index](00_index.md)**

This index maps every SIA control across all regulatory frameworks and standards simultaneously.

| Hazard ID | Control | Description | EU AI Act | GDPR | HIPAA | ISO 42001 |
| --- | --- | --- | --- | --- | --- | --- |
| **HZ-01** | `REDACT_OR_HASH` | Dynamic ingress sanitizer that redacts general PII befo… | Art. 10 (Data Governance) | Art. 5(1)(c) (Data Minimisation) | §164.514 (De-identification) | Clause 6.1.2 (Information Security Risk) |
| **HZ-02** | `REQUIRE_TRACEABILITY_HASH` | Traceability engine hashes all system interactions with… | Art. 12 (Record-Keeping) | Art. 30 (Records of Processing) | §164.312(b) (Audit Controls) | Clause 9.1 (Monitoring & Measurement) |
| **HZ-03** | `APPEND_WATERMARK` | Transparency engine automatically appends clear machine… | Art. 13 (Transparency) | Art. 22 (Automated Decision-Making) | N/A | Clause 8.6 (Human Oversight) |
| **HZ-04** | `REQUIRE_HUMAN_VETO` | Human-in-the-Loop gate triggering an HTTP 202 to pause … | Art. 14.4 (Human Oversight — Annex III) | Art. 22 (Automated Decision-Making) | §164.306(a) (Administrative Safeguards) | Clause 8.6 (Human Oversight) |
| **HZ-05** | `MONITOR_CONFIDENCE_DRIFT` | Active post-market monitoring using statistical heurist… | Art. 72 (Post-Market Monitoring) | Art. 35 (DPIA — ongoing review) | §164.308(a)(8) (Evaluation) | Clause 10.1 (Continual Improvement) |
| **HZ-06** | `BLOCK_AND_REWRITE` | Truth Razor grounding engine requires a minimum confide… | Art. 15.1 (Accuracy & Robustness) | Art. 5(1)(d) (Accuracy) | §164.306(a)(1) (Integrity) | Clause 8.5 (AI System Verification) |
| **HZ-07** | `BLOCK_PROMPT_INJECTION` | Adversarial intent classifier that blocks inputs matchi… | Art. 15.3 (Cybersecurity) | Art. 32 (Security of Processing) | §164.312(a) (Access Control) | Clause 8.3 (Adversarial Robustness) |
| **HZ-08** | `MONITOR_ANOMALIES` | Automated risk management control detecting extreme pay… | Art. 72 (Post-Market Monitoring) | Art. 32 (Security of Processing) | §164.308(a)(6) (Incident Response) | Clause 10.2 (Incident Management) |
| **HZ-09** | `BLOCK_PROHIBITED_DOMAINS` | Ingress semantic filter that proactively drops interact… | Art. 5 (Prohibited AI Practices) | Art. 9 (Special Categories — Biometric) | N/A | Clause 4.2 (Interested Parties — Ethical Constraints) |
| **HZ-10** | `ENFORCE_TOKEN_LIMIT` | Limits the maximum number of tokens per request to prev… | Art. 15.3 (Cybersecurity & Availability) | Art. 32(1)(b) (Availability) | §164.312(a)(2)(ii) (Emergency Access) | Clause 7.1 (Resources) |
| **HZ-11** | `ENFORCE_RATE_LIMIT` | In-memory sliding window rate limiter enforcing maximum… | Art. 15.3 (Cybersecurity) | Art. 32 (Security of Processing) | §164.312(a) (Access Control) | Clause 8.3 (Adversarial Robustness) |
| **HZ-12** | `BLOCK_PROHIBITED_PRACTICES` | Proactively drops interactions matching unequivocally p… | Art. 5(1)(a-c) (Prohibited Practices) | Art. 5(1)(a) (Lawfulness, Fairness) | N/A | Clause 4.2 (Ethical Constraints) |
| **HZ-13** | `BLOCK_SPECIAL_CATEGORY_DATA` | Blocks inputs containing health, genetic, racial, or po… | Art. 10.5 (Special Category Data) | Art. 9 (Special Category Data) | §164.308(a)(3) (Workforce Authorization) | Clause 8.4 (AI System Lifecycle) |
| **HZ-14** | `APPEND_DISCLAIMER` | Dynamically appends Annex III specific disclaimers (e.g… | Art. 13 (Transparency & Information) | Art. 13 (Right to Information) | §164.520 (Notice of Privacy Practices) | Clause 7.4 (Communication) |
| **HZ-15** | `VALIDATE_INPUT_SCHEMA` | Validates input token length and encodings (e.g., utf-8… | Art. 15.1 (Accuracy & Robustness) | Art. 32 (Security of Processing) | §164.312(e) (Transmission Security) | Clause 8.5 (AI System Verification) |
| **HZ-16** | `REQUIRE_MINIMUM_CONFIDENCE` | Enforces a minimum confidence threshold on outputs befo… | Art. 15.1 (Accuracy) | Art. 5(1)(d) (Accuracy) | §164.306(a)(1) (Integrity) | Clause 8.5 (Verification & Validation) |
| **HZ-17** | `REQUIRE_RAG_GROUNDING` | Ensures outputs are grounded in approved Retrieval-Augm… | Art. 15.1 (Accuracy & Robustness) | Art. 5(1)(d) (Accuracy) | N/A | Clause 8.5 (Verification) |
| **HZ-18** | `REQUIRE_SOURCE_ATTRIBUTION` | Requires inline attribution/citation of the exact knowl… | Art. 13 (Transparency) | Art. 5(1)(a) (Lawfulness) | N/A | Clause 7.4 (Communication) |
| **HZ-19** | `BLOCK_COPYRIGHTED_SOURCES` | Blocks sources outside of the explicitly allowlisted in… | Art. 53 (GPAI — Copyright) | N/A | N/A | Clause 4.2 (Legal Constraints) |
| **HZ-20** | `APPEND_MACHINE_READABLE_MARKER` | Injects HTTP headers marking content as AI-generated fo… | Art. 50.1 (AI-Generated Content Disclosure) | N/A | N/A | Clause 7.4 (Communication) |
| **HZ-21** | `BLOCK_SYNTHETIC_MEDIA_REQUEST` | Blocks requests for deepfakes, face swaps, or synthetic… | Art. 50.2 (Synthetic Media) | Art. 9 (Biometric Data) | N/A | Clause 4.2 (Ethical Constraints) |
| **HZ-22** | `PSEUDONYMIZE_VAULT` | Zero-Trust Supervisory Mesh encrypts identifiers, separ… | Art. 10.5 (Special Category Data) | Art. 9 (Special Categories) | §164.312 (Technical Safeguards) | Clause 8.4 (AI System Lifecycle) |
| **HZ-23** | `REGULATORY_ROUTER` | SIA Regulatory Router applies location-based 'Strictest… | Art. 9 (Quality Management) | Art. 17 (Right to Erasure), Art. 5(1)(e) (Storage Limitation) | §164.530(j) (Retention — 6 years) | Clause 9.1 (Monitoring & Measurement) |
| **HZ-24** | `VALIDATE_PROFILE_MATCH` | Active validation mapping clinical subject demographics… | Art. 10.2 (Dataset Quality) | Art. 5(1)(a) (Fairness) | N/A | Clause 8.4 (AI System Lifecycle), Annex B.7 (Data Governance) |
| **HZ-25** | `BLOCK_OOD_PAYLOAD` | Semantic distance filter calculating input distance to … | Art. 15.1 (Accuracy & Robustness) | Art. 32 (Security of Processing) | N/A | Clause 8.5 (AI System Verification), Annex B.8 (AI System Robustness) |
| **HZ-26** | `APPEND_CONFIDENCE_TELEMETRY` | Exposes system confidence ratings and appends clinician… | Art. 13 (Transparency), Art. 14 (Human Oversight) | Art. 22 (Automated Decision-Making) | N/A | Clause 8.6 (Human Oversight), Annex B.6 (Human Oversight) |