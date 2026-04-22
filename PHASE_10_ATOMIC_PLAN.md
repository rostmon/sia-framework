# Implementation Plan: Atomic Governance & Comprehensive Validation

To ensure absolute regulatory precision, we need to break down the high-level configurations into atomic, independent rules mapping strictly to specific paragraphs across *all applicable* EU AI Act Articles. Furthermore, we must expand our `test_poc.py` to trigger *every single rule* in the YAML to generate a comprehensive, 100% coverage Validation Report.

## 🛠️ Proposed Changes

### 1. Atomic Configurations Across All Articles (`configs/eu_ai_act_full.yaml`)
We will refactor the configuration into atomic rules:
*   **Article 10.2(f) (Bias):** Atomic rule for `BLOCK_PROHIBITED_DOMAINS`.
*   **Article 10.3 (Data Quality):** Atomic rule for `STRIP_PII`.
*   **Article 12.1 (Record-Keeping):** Atomic rule for `REQUIRE_TRACEABILITY_HASH`.
*   **Article 13.1 (Transparency):** Atomic rule for `APPEND_WATERMARK`.
*   **Article 14.4 (Human Oversight):** Atomic rule for `REQUIRE_HUMAN_VETO` based on Annex III mappings.
*   **Article 15.1 (Accuracy Metrics):** Atomic rule for `REQUIRE_MINIMUM_CONFIDENCE: 0.85`.
*   **Article 15.3 (Resilience/Factuality):** Two atomic rules: `REQUIRE_RAG_GROUNDING` and fallback `BLOCK_AND_REWRITE`.

### 2. Upgrading the Engine (`src/sia/core/engine.py`)
The `RuleEvaluationEngine` will be updated to evaluate these atomic rules sequentially. If confidence fails, it logs an Article 15.1 violation. If RAG grounding fails, it logs an Article 15.3 violation and executes the fallback rewrite.

### 3. Comprehensive Validation Suite (`tests/test_poc.py`)
I will completely rewrite the PoC to act as an automated Integration Test Suite. It will execute 6 distinct scenarios to trigger every rule in the Governance-as-Code schema:
1.  **Test 1 (Article 10.2f):** Prompt containing prohibited bias domains.
2.  **Test 2 (Article 10.3):** Prompt containing PII.
3.  **Test 3 (Article 14.4):** Prompt containing Annex III High-Risk keywords.
4.  **Test 4 (Article 15.1/15.3):** Output with low confidence / hallucination.
5.  **Test 5 (Article 13.1):** Compliant prompt (verifying Watermark is appended).
6.  **Test 6 (Article 12.1):** Verification that all above tests generated cryptographic trace hashes.

### 4. Objective Evidence Generation
After running the comprehensive suite, we will execute `reporter.py` to generate a heavily populated `ANNEX_IV_EVIDENCE.md` artifact demonstrating 100% rule coverage.
