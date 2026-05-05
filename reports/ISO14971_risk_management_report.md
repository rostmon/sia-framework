# ISO 14971 Risk Management Report
**Date Generated:** 2026-05-05 14:32:59
**System:** SIA Framework (Sovereign Systemic Integrity Architecture)

## 1. Intended Use and Scope
This document details the risk management activities for the SIA Framework. Because SIA acts as a middleware intended to govern High-Risk LLMs, its risk management focuses heavily on mitigating the hazards introduced by non-deterministic AI models in accordance with ISO 14971 and EU AI Act Article 9.

## 2. Risk Acceptability Criteria
Risks are evaluated using a standard matrix combining **Severity of Harm** (1-5) and **Probability of Occurrence** (1-5). The Risk Priority Number (RPN) is calculated as `Severity x Probability`.
- **Acceptable (RPN 1-8):** No further mitigation required.
- **ALARP (As Low As Reasonably Practicable) (RPN 9-15):** Mitigation required unless technical limitations prevent it.
- **Unacceptable (RPN 16-25):** Mandatory mitigation required before deployment.

## 3. Hazard Identification & Risk Traceability Matrix
| Hazard ID | Failure Mode | Hazard Description | Pre-Mitigation RPN | SIA Mitigation | Mitigation Description | Residual RPN | Acceptability |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **HZ-04** | Automated High-Risk Decision | Discrimination, Loss of Rights. | **25** (S:5, P:5) | `REQUIRE_HUMAN_VETO` | Human-in-the-Loop gate triggering an HTTP 202 to pause execution for a mandatory human signature on Annex III tasks. | **5** (S:5, P:1) | 🟢 Acceptable |
| **HZ-01** | PII Leakage | Data Breach, GDPR violation. | **20** (S:4, P:5) | `STRIP_PII` | Dynamic regex-based ingress sanitizer that redacts sensitive personal data before network transit. | **4** (S:4, P:1) | 🟢 Acceptable |
| **HZ-09** | Unacceptable Risk Practice | Violation of Article 5 (e.g., social scoring, biometric categorization). | **20** (S:5, P:4) | `BLOCK_PROHIBITED_DOMAINS` | Ingress semantic filter that proactively drops interactions matching explicitly prohibited AI use-cases. | **5** (S:5, P:1) | 🟢 Acceptable |
| **HZ-06** | Hallucination / Confabulation | User harm, misdiagnosis. | **16** (S:4, P:4) | `BLOCK_AND_REWRITE` | Truth Razor grounding engine requires a minimum confidence threshold, rewriting failures into a safe deterministic fallback. | **4** (S:4, P:1) | 🟢 Acceptable |
| **HZ-07** | Prompt Injection | Unintended system behavior, jailbreak. | **16** (S:4, P:4) | `BLOCK_PROMPT_INJECTION` | Adversarial intent classifier that blocks inputs matching known jailbreak or instruction-override patterns. | **4** (S:4, P:1) | 🟢 Acceptable |
| **HZ-13** | Unauthorized Sensitive Data Usage | Processing special categories of personal data (Article 10.5). | **16** (S:4, P:4) | `BLOCK_SPECIAL_CATEGORY_DATA` | Blocks inputs containing health, genetic, racial, or political data unless strictly necessary. | **4** (S:4, P:1) | 🟢 Acceptable |
| **HZ-16** | Low Quality Output | System generates inaccurate or non-robust outputs (Article 15.1). | **16** (S:4, P:4) | `REQUIRE_MINIMUM_CONFIDENCE` | Enforces a minimum confidence threshold on outputs before they can be returned. | **4** (S:4, P:1) | 🟢 Acceptable |
| **HZ-17** | Ungrounded Response | System generates facts without grounding in verified context. | **16** (S:4, P:4) | `REQUIRE_RAG_GROUNDING` | Ensures outputs are grounded in approved Retrieval-Augmented Generation sources. | **4** (S:4, P:1) | 🟢 Acceptable |
| **HZ-02** | Lack of Traceability | Non-compliance, lack of accountability. | **15** (S:3, P:5) | `REQUIRE_TRACEABILITY_HASH` | Traceability engine hashes all system interactions with SHA-256 into the immutable audit ledger. | **3** (S:3, P:1) | 🟢 Acceptable |
| **HZ-05** | Data Drift | Model degradation over time, reduced accuracy. | **15** (S:3, P:5) | `MONITOR_CONFIDENCE_DRIFT` | Active post-market monitoring using statistical heuristics to track shifts in input distributions against baselines. | **6** (S:3, P:2) | 🟢 Acceptable |
| **HZ-10** | Resource Exhaustion | Denial of Service, performance degradation. | **15** (S:3, P:5) | `ENFORCE_TOKEN_LIMIT` | Limits the maximum number of tokens per request to prevent infrastructure exhaustion and buffer overflows. | **3** (S:3, P:1) | 🟢 Acceptable |
| **HZ-11** | High-Frequency Abuse | Brute force attacks, service unavailability. | **15** (S:3, P:5) | `ENFORCE_RATE_LIMIT` | In-memory sliding window rate limiter enforcing maximum requests per minute per client session. | **3** (S:3, P:1) | 🟢 Acceptable |
| **HZ-12** | Subliminal/Exploitative Practice | Violation of Article 5 (e.g., subliminal manipulation, exploiting vulnerabilities, RTBI). | **15** (S:5, P:3) | `BLOCK_PROHIBITED_PRACTICES` | Proactively drops interactions matching unequivocally prohibited AI practices. | **5** (S:5, P:1) | 🟢 Acceptable |
| **HZ-03** | Automation Bias | Overreliance, user error due to trusting AI blindly. | **12** (S:3, P:4) | `APPEND_WATERMARK` | Transparency engine automatically appends clear machine and human-readable warnings to compliant outputs. | **3** (S:3, P:1) | 🟢 Acceptable |
| **HZ-08** | Data Poisoning / Anomaly | Systematic failure due to corrupted input distribution. | **12** (S:4, P:3) | `MONITOR_ANOMALIES` | Automated risk management control detecting extreme payload sizes and unusual non-standard character density. | **4** (S:4, P:1) | 🟢 Acceptable |
| **HZ-14** | User Misunderstanding | User relies on AI output without understanding capabilities/limitations (Article 13). | **12** (S:3, P:4) | `APPEND_DISCLAIMER` | Dynamically appends Annex III specific disclaimers (e.g., healthcare, legal) to output. | **3** (S:3, P:1) | 🟢 Acceptable |
| **HZ-15** | Malformed Input / System Crash | System receives malformed data leading to crashes or unpredictable state. | **12** (S:3, P:4) | `VALIDATE_INPUT_SCHEMA` | Validates input token length and encodings (e.g., utf-8) per request. | **3** (S:3, P:1) | 🟢 Acceptable |
| **HZ-19** | Copyright Infringement | System outputs copyrighted material in violation of EU law (Article 53). | **12** (S:3, P:4) | `BLOCK_COPYRIGHTED_SOURCES` | Blocks sources outside of the explicitly allowlisted internal KB or creative commons. | **3** (S:3, P:1) | 🟢 Acceptable |
| **HZ-18** | Unverifiable Source | User cannot trace the source of information provided by the AI. | **10** (S:2, P:5) | `REQUIRE_SOURCE_ATTRIBUTION` | Requires inline attribution/citation of the exact knowledge base source. | **2** (S:2, P:1) | 🟢 Acceptable |
| **HZ-20** | Deepfake Ambiguity | Users unaware that content is AI-generated (Article 50.1). | **10** (S:2, P:5) | `APPEND_MACHINE_READABLE_MARKER` | Injects HTTP headers marking content as AI-generated for machine parsability. | **2** (S:2, P:1) | 🟢 Acceptable |
| **HZ-21** | Unauthorized Deepfake Generation | Generation of synthetic media without disclosure (Article 50.2). | **9** (S:3, P:3) | `BLOCK_SYNTHETIC_MEDIA_REQUEST` | Blocks requests for deepfakes, face swaps, or synthetic voice impersonations. | **3** (S:3, P:1) | 🟢 Acceptable |

## 4. Conclusion
All identified hazards have been mitigated via deterministic `Governance-as-Code` rules implemented in the SIA Framework configuration. The residual risks for all identified failure modes have been reduced to an Acceptable level (RPN <= 8).