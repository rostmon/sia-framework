# Changelog

All notable changes to the SIA Framework are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.1.0] — 2026-04-22 — Initial Public Release

### 🎉 Phase 5 Complete — Full EU AI Act Conformity Lifecycle

This release marks the completion of the full five-phase implementation of the SIA Framework, delivering a production-grade Governance-as-Code system covering the EU AI Act (Regulation EU 2024/1689).

---

### Added

#### Core Governance Engine
- `RuleEvaluationEngine` — Three-tier taxonomy (runtime_gate / deployment_assertion / governance_doc)
- `EUAIActConfig` — Pydantic-validated YAML config loading with full type safety
- `GovernanceCache` — SHA-256 prompt hash deduplication cache (configurable LRU)
- `SIAConfigError` — Hard startup failure on deployment assertion violations

#### Ingress Layer
- `ContextualIngressOrchestrator` — Pipeline coordinator for all ingress governance
- `IntentClassifier` — Hybrid keyword + optional LLM zero-shot Annex III risk classification
- `DataSanitizer` — PII redaction (email, SSN) before model exposure (Art. 10.3)
- Prompt injection detection — Pattern-based jailbreak and override detection (Art. 15.4)

#### Egress Layer
- `DeterministicEgressValidator` — Confidence gate, RAG grounding, copyright check
- Hallucination fallback rewrite — Deterministic response replacement (Art. 15.1/3)
- AI watermark footer — Mandatory transparency disclosure (Art. 13.1)
- Contextual disclaimers — Dynamic healthcare/employment/legal disclaimers (Art. 13.2)
- Machine-readable AI marker — `X-SIA-AI-Generated: true` HTTP header (Art. 50.1)

#### SIAClient & Adapters
- `SIAClient` — Main governed client with `chat()`, `achat()`, `astream()` methods
- `SIAResponse` — Typed response with `action`, `http_status`, `risk_score`, `trace_hash`
- `@governed` decorator — Zero-refactor wrapping for sync, async, and async-generator functions
- `OpenAIAdapter` — Full sync/async/streaming support with logprob confidence normalization
- `AnthropicAdapter` — Claude sync support with stop-reason confidence mapping
- `HuggingFaceAdapter` — Hosted Inference API + local transformers pipeline
- `MockAdapter` — Deterministic test adapter for CI without API keys

#### Traceability (Article 12)
- `AuditLedger` — Append-only SHA-256 JSONL cryptographic ledger
- `ReasoningExtractor` — Chain-of-thought path extraction from model raw responses
- `ComplianceReporter` — Automated Annex IV Technical Documentation evidence generator

#### Regulatory (Article 43)
- `ConformityAssessor` — Interactive Article 43 conformity assessment with persistent state
- `ConformityCertificate` — JSON-LD conformity certificate with SHA-256 mock signature

#### Monitoring & Observability
- `MetricsCollector` — Reads `audit_ledger.jsonl` to compute all runtime governance metrics
- `SIA Monitoring API` — FastAPI server with REST + WebSocket metrics streaming
- Live Dashboard — Self-contained HTML dashboard at `http://127.0.0.1:8001`
- Anomaly detection — 5 consecutive block alert (Art. 72.1)
- Annex IV evidence report endpoint
- Conformity certificate endpoint

#### Integrations
- `SIAMiddleware` — FastAPI ASGI middleware for zero-code governance

#### CLI
- `sia init` — Industry preset config bootstrapper (general, healthcare, hr, finance)
- `sia validate` — YAML governance config linter

#### Configuration
- `configs/eu_ai_act_full.yaml` — Master ruleset: Articles 5, 9, 10, 11, 12, 13, 14, 15, 50, 53, 72
- `configs/conformity_checklist.yaml` — Article 43/Annex VI conformity checklist
- Industry blueprints: `healthcare_v1.yaml`, `hr_recruitment_v1.yaml`, `finance_v1.yaml`, `general_transparency.yaml`

#### Webhooks
- `WebhookDispatcher` — Article 14.4 HITL notification dispatch (async + sync)

#### Documentation
- `docs/SYSTEM_DESCRIPTION.md` — Annex IV system description
- `docs/RISK_MANAGEMENT_SUMMARY.md` — Article 9 hazard matrix
- `docs/TRACEABILITY.md` — Article 12 traceability evidence
- `docs/SIA_VALIDATION_REPORT.md` — Article 15 validation evidence
- Comprehensive `README.md` with full architecture, quickstart, and API reference

---

### EU AI Act Articles Implemented

| Article | Coverage |
|---------|----------|
| Art. 5 | Prohibited practices: subliminal, social scoring, biometrics, exploitation |
| Art. 9 | Risk management deployment assertions |
| Art. 10.2f | Bias/hate speech blocking |
| Art. 10.3 | PII sanitization (TRANSFORM, not block) |
| Art. 10.5 | Special category data blocking |
| Art. 11 | Technical documentation deployment assertion |
| Art. 12 | SHA-256 cryptographic audit ledger |
| Art. 13.1 | AI-generated watermark |
| Art. 13.2 | Domain-specific disclaimers |
| Art. 14.4 | Human veto (HTTP 202) + HITL webhook |
| Art. 15.1 | Minimum confidence enforcement |
| Art. 15.3 | RAG grounding, attribution, copyright |
| Art. 15.4 | Prompt injection / jailbreak defense |
| Art. 50.1 | Machine-readable AI content marker |
| Art. 50.2 | Synthetic media / deepfake blocking |
| Art. 53 | GPAI copyright compliance |
| Art. 72 | Post-market anomaly monitoring |
| Art. 43 | Conformity assessment lifecycle + certificate |

---

### Known Limitations (v0.1.0)

- `DataSanitizer` uses basic regex patterns; production deployments should integrate Microsoft Presidio
- `ConformityCertificate` uses SHA-256 mock signatures; production deployments require RSA/PKI infrastructure
- `AnthropicAdapter` does not yet support `agenerate()` / `astream()` — async support planned for v0.2.0
- `GovernanceCache` is in-process memory only; no Redis/distributed cache support yet

---

*Initial release — designed and implemented by the Sovereign AI Team.*
