# SIA Framework Implementation Tasks

## Phase 1: Core Framework Foundation & Governance-as-Code (GaC) Engine
- `[x]` Initialize Python project structure (`src/sia`, `tests/`, `configs/`).
- `[x]` Setup basic project files (`pyproject.toml` or `requirements.txt`).
- `[x]` Create `configs/sia_logic_gate.yaml` with sample rules.
- `[x]` Implement Config Parser (`sia.core.config`) using `Pydantic` to validate Governance logic.
- `[x]` Implement Rule Evaluation Engine (`sia.core.engine`) to process simple logic rules.

## Phase 2: The Sovereign Stack - Core Modules
### Module 1: Contextual Ingress Orchestrator
- `[x]` Implement Intent Classification stub.
- `[x]` Implement Data Sanitization using `Presidio` (or similar).
- `[x]` Implement Pre-emptive Veto logic.

### Module 2: Forensic Traceability Engine
- `[x]` Implement Reasoning-Path Extraction capture.
- `[x]` Implement Cryptographic Anchoring (`hashlib`).
- `[x]` Implement Audit Ledger (SQLite/PostgreSQL integration).

### Module 3: Deterministic Egress Validator
- `[x]` Implement Fact & RAG Verification stub.
- `[x]` Implement Truth Razor (Hallucination Filter) and `BLOCK_AND_REWRITE` mechanism.
- `[x]` Implement Integrity Signature appending.

## Phase 3: Integration & API Layer
- `[x]` Create SIA Proxy/Middleware interface.
- `[x]` Implement FastAPI Sidecar.

## Phase 4: Testing & Proof of Concept (PoC)
- `[x]` Setup Mock LLM.
- `[x]` Create and run Adversarial Tests.
- `[x]` End-to-End run verification.

## Phase 5: EU AI Act Governance-as-Code Translation
- `[x]` Create comprehensive `configs/eu_ai_act_full.yaml` with per-environment granularity and Annex III categorization.
- `[x]` Expand `src/sia/core/config.py` Pydantic models for nested Article/Annex tracking.
- `[x]` Upgrade `src/sia/core/engine.py` to evaluate new rules.
- `[x]` Update Ingress/Egress layers and FastAPI route to support HTTP 202 Accepted for Human Signature (HITL).
- `[x]` Update `test_poc.py` to demonstrate the new EU AI Act schema.

## Phase 6: EU AI Act Paragraph-Level Breakdown
- `[ ]` Update `configs/eu_ai_act_full.yaml` to include nested paragraphs.
- `[ ]` Update `src/sia/core/config.py` to handle the `Article -> Paragraph -> Rule` hierarchy.
- `[ ]` Update `src/sia/core/engine.py` to evaluate and return specific paragraph references.
- `[ ]` Update `src/sia/main.py` and `tests/test_poc.py` to log specific paragraph triggers.
- `[ ]` Update `TRACEABILITY.md` matrix.

## Phase 7: Compliance Evidence Pipeline
- `[x]` Implement `src/sia/traceability/reporter.py` to parse `audit_ledger.jsonl`.
- `[x]` Implement aggregation logic for Articles 10, 14, and 15 metrics.
- `[x]` Implement Markdown generation for `ANNEX_IV_EVIDENCE.md`.
- `[x]` Run pipeline and verify output artifact.

## Phase 8: Compliance Gap Analysis & Validation Reporting
- `[ ]` Generate `GAP_ANALYSIS.md` mapping Annex IV to current artifacts.
- `[ ]` Draft `SYSTEM_DESCRIPTION.md` to close Intended Use and Architecture gaps.
- `[ ]` Draft `RISK_MANAGEMENT_SUMMARY.md` to close Article 9 gaps.
- `[x]` Compile Master `SIA_VALIDATION_REPORT.md`.
- `[x]` Commit all documentation to repository.

## Phase 9: Detailed Documentation Expansion
- `[x]` Expand `SYSTEM_DESCRIPTION.md` (Architecture, Data Flow, Users).
- `[x]` Expand `RISK_MANAGEMENT_SUMMARY.md` (Hazard Matrix, Acceptability Criteria).
- `[x]` Expand `SIA_VALIDATION_REPORT.md` (Validation Protocol, Acceptance Criteria).
- `[x]` Commit detailed documentation to repository.

## Phase 10: Atomic Configuration & Comprehensive Validation
- `[x]` Refactor `configs/eu_ai_act_full.yaml` to purely atomic rules across all articles.
- `[x]` Update `src/sia/core/engine.py` to evaluate atomic rules.
- `[x]` Expand `tests/test_poc.py` to run comprehensive 6-scenario integration suite.
- `[x]` Run test suite to populate ledger.
- `[x]` Generate comprehensive `ANNEX_IV_EVIDENCE.md`.

## Phase 11: Comprehensive Article 5, 13.2, and 15.4 Integration
- `[ ]` Inject Article 5, 13.2, and 15.4 atomic rules into `eu_ai_act_full.yaml`.
- `[ ]` Update `orchestrator.py` and `engine.py` to enforce new logic gates.
- `[ ]` Expand `test_poc.py` with adversarial/prohibited scenarios.
- `[ ]` Update `reporter.py` to track new blocks.
- `[ ]` Run validation and commit to repository.
