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
- `[ ]` Implement `src/sia/traceability/reporter.py` to parse `audit_ledger.jsonl`.
- `[ ]` Implement aggregation logic for Articles 10, 14, and 15 metrics.
- `[ ]` Implement Markdown generation for `ANNEX_IV_EVIDENCE.md`.
- `[ ]` Run pipeline and verify output artifact.
