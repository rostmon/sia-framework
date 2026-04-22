# Implementation Plan: EU AI Act Paragraph-Level Configuration

Based on your request, we will increase the granularity of our Governance-as-Code schema by breaking down the high-level Articles into specific, actionable **paragraph-level requirements** corresponding directly to the official legal text of the EU AI Act.

## ⚖️ Background Context
Currently, our `configs/eu_ai_act_full.yaml` groups rules broadly under "Article 10" or "Article 14". While functional, a true compliance framework must tie technical interventions directly to specific paragraphs (e.g., Article 10.2(f) regarding bias examination). 

## 🛠️ Proposed Changes

### [MODIFY] `configs/eu_ai_act_full.yaml`
We will rewrite the YAML file to map technical logic to precise paragraphs:

*   **Article 10: Data and Data Governance**
    *   `article_10_2_f` (Examination of Biases): Enforces `BLOCK_PROHIBITED_DOMAINS` to prevent biased inferences.
    *   `article_10_3` (Error-Free & Representative): Enforces `STRIP_PII` to ensure clean, compliant data structures without exposing unauthorized personal records.
    *   `article_10_5` (Safeguards for Special Categories): Technically enforces redaction of special categories of data if detected.
*   **Article 12: Record-Keeping**
    *   `article_12_1` (Automatic Recording of Events): Triggers `REQUIRE_TRACEABILITY_HASH` for all high-risk interactions.
    *   `article_12_2` (Traceability Lifetime): Enforces `LOG_RETENTION_POLICY`.
*   **Article 13: Transparency**
    *   `article_13_1` (Instructions for Use): Appends `APPEND_WATERMARK` ensuring users are aware of AI interaction.
*   **Article 14: Human Oversight**
    *   `article_14_1` (Effective Human Intervention): Identifies Annex III categories.
    *   `article_14_4` (Human Override): Enforces `REQUIRE_HUMAN_VETO` (HTTP 202) for flagged high-risk actions.
*   **Article 15: Accuracy, Robustness and Cybersecurity**
    *   `article_15_1` (Appropriate Level of Accuracy): Enforces `REQUIRE_RAG_GROUNDING` and `MIN_CONFIDENCE`.
    *   `article_15_3` (Resilience against Errors): Enforces `BLOCK_AND_REWRITE` to catch hallucinations.

### [MODIFY] `src/sia/core/config.py` & `src/sia/core/engine.py`
Because the nested structure changes from `articles -> rules` to `articles -> paragraphs -> rules`, we will update the `Pydantic` models and the engine's evaluation loops to parse this deeper tree.

---

## ✅ Verification Plan

1. **Schema Validation:** Ensure `Pydantic` successfully loads the deeply nested YAML.
2. **Traceability:** Rerun the `test_poc.py` script. The logs will now explicitly state which *paragraph* triggered an intervention (e.g., "Blocked by Article 14.4" instead of just "Article 14").
3. **Update Artifacts:** Re-generate the `TRACEABILITY.md` to reflect the exact paragraph numbers for absolute audit readiness.
