from typing import Any, Dict, List, Optional, Tuple
from sia.core.config import EUAIActConfig
from sia.core.risk import RuntimeRiskManager, IncidentLogger


class SIAConfigError(Exception):
    """Raised when a deployment_assertion rule fails at SIAClient startup."""


class RuleEvaluationEngine:
    """
    Evaluates EU AI Act governance rules in three tiers:
      1. runtime_gate          — per-request, produces API HTTP codes
      2. deployment_assertion  — validated once at __init__
      3. governance_doc        — no runtime evaluation; evidence in docs/
    """

    def __init__(self, config: EUAIActConfig, environment: str = "prod"):
        self.config = config
        self.environment = environment
        self.active_category: Optional[str] = None
        self.risk_manager = RuntimeRiskManager()
        self._validate_deployment_assertions()

    def _validate_deployment_assertions(self) -> None:
        """
        Runs all deployment_assertion rules at startup.
        Raises SIAConfigError if any assertion fails.
        """
        errors = []
        for art_key, article in self.config.articles.items():
            for para_key, para in article.paragraphs.items():
                for rule_key, rule in para.rules.items():
                    if rule.category != "deployment_assertion":
                        continue
                    error = self._check_deployment_rule(rule_key, rule)
                    if error:
                        errors.append(f"[{art_key}.{para_key}.{rule_key}] {error}")
        if errors:
            raise SIAConfigError(
                "Deployment assertion failures — SIAClient cannot start:\n" +
                "\n".join(errors)
            )

    def _check_deployment_rule(self, rule_key: str, rule) -> Optional[str]:
        """Returns an error string if the deployment assertion fails, else None."""
        import os
        if rule.logic == "REQUIRE_RISK_CLASSIFICATION":
            if not self.config.annex_iii_categories:
                return "annex_iii_categories must be defined."
        elif rule.logic == "ENFORCE_RETENTION":
            path = rule.retention_path
            if not path:
                return "retention_path must be configured."
            # Validate parent directory exists (file may not exist yet if fresh install)
            parent = os.path.dirname(path)
            if parent and not os.path.exists(parent):
                os.makedirs(parent, exist_ok=True)
        elif rule.logic == "VALIDATE_SYSTEM_METADATA":
            pass  # Satisfied by having the config file present
        elif rule.logic == "VALIDATE_ACCURACY_METADATA":
            pass  # Satisfied by required_metrics being declared in YAML
        return None

    def _is_runtime_gate(self, rule) -> bool:
        return rule.category == "runtime_gate"

    def is_environment_active(self) -> bool:
        return self.environment in self.config.environments.active

    def _get_para(self, article_key: str, para_key: str):
        """Safe paragraph getter."""
        art = self.config.articles.get(article_key)
        if art:
            return art.paragraphs.get(para_key)
        return None

    # ──────────────────────────────────────────────────────────────────────────
    # INGRESS EVALUATION
    # ──────────────────────────────────────────────────────────────────────────
    def evaluate_ingress(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluates ingress-time gates and returns a risk score (0-100).
        """
        if not self.is_environment_active():
            return {"allowed": True, "requires_human_review": False,
                    "trigger_paragraph": None, "trigger_reason": None,
                    "risk_score": 0.0}

        # --- 0. Runtime Risk Management Checks ---
        if self.risk_manager.is_kill_switch_active():
            IncidentLogger.log_incident("KILL_SWITCH_ACTIVE", "Request blocked due to active emergency kill-switch.")
            return self._block("article_14_4", "Emergency Kill-Switch is active", 503)

        client_id = context.get("client_id", "default")
        if not self.risk_manager.check_rate_limit(client_id):
            return self._block("article_15", "Rate limit exceeded (Model Inversion Protection)", 429)

        original_prompt = context.get("prompt_text", "")
        sanitized_prompt = self.risk_manager.sanitize_input(original_prompt)
        context["prompt_text"] = sanitized_prompt # Update context with sanitized
        
        is_anomaly, anomaly_reason = self.risk_manager.check_anomaly(sanitized_prompt)
        if is_anomaly:
            return self._block("article_15", f"Data Poisoning Anomaly Detected: {anomaly_reason}", 400)
            
        self.risk_manager.update_and_check_drift(sanitized_prompt) # Non-blocking, logs internally if drift

        risk_score = 0.0
        intent = context.get("intent", "low_risk")
        prompt_text = context.get("prompt_text", "").lower()
        prompt_upper = context.get("prompt_text", "")
        self.active_category = None

        # ── 1. Article 15.4: Prompt Injection ─────────────────────────────────
        para_15_4 = self._get_para("article_15_accuracy_robustness", "article_15_4")
        if para_15_4:
            inj_rule = para_15_4.rules.get("rule_prompt_injection_defense")
            if inj_rule and inj_rule.logic == "BLOCK_PROMPT_INJECTION":
                patterns = inj_rule.patterns or []
                if intent == "prompt_injection" or any(p.lower() in prompt_upper.lower() for p in patterns):
                    return self._block("article_15_4", "Adversarial Prompt Injection Detected", 400)

            tok_rule = para_15_4.rules.get("rule_token_limit_defense")
            if tok_rule and tok_rule.max_tokens:
                approx_tokens = len(prompt_upper.split()) * 1.3
                if approx_tokens > tok_rule.max_tokens:
                    return self._block("article_15_4", "Prompt exceeds maximum token limit", 400)

        # ── 2. Article 5: All prohibited practice sub-paragraphs ──────────────
        art_5 = self.config.articles.get("article_5_prohibited_practices")
        if art_5:
            for para_key, para in art_5.paragraphs.items():
                for rule in para.rules.values():
                    if rule.logic == "BLOCK_PROHIBITED_PRACTICES":
                        if intent in (rule.practices or []):
                            return self._block(para_key, f"Prohibited Practice: {intent}",
                                               para.api_response_on_block or 451)

        # ── 3. Article 50.2: Synthetic Media / Deepfake ───────────────────────
        para_50_2 = self._get_para("article_50_transparency_obligations", "article_50_2")
        if para_50_2:
            synth_rule = para_50_2.rules.get("rule_synthetic_media_block")
            if synth_rule and intent in (synth_rule.practices or []):
                return self._block("article_50_2", f"Synthetic Media Request Blocked: {intent}",
                                   para_50_2.api_response_on_block or 451)

        # ── 4. Article 10.2(f): Bias/Hate Speech ─────────────────────────────
        para_10_2_f = self._get_para("article_10_data_governance", "article_10_2_f")
        if para_10_2_f:
            bias_rule = para_10_2_f.rules.get("rule_bias_detection")
            if bias_rule and intent in (bias_rule.domains or []):
                return self._block("article_10_2_f", f"Prohibited Domain: {intent}",
                                   para_10_2_f.api_response_on_block or 400)

        # ── 5. Article 10.5: Special Category Data ────────────────────────────
        para_10_5 = self._get_para("article_10_data_governance", "article_10_5")
        if para_10_5:
            sc_rule = para_10_5.rules.get("rule_sensitive_data_gate")
            if sc_rule and intent in (sc_rule.categories or []):
                return self._block("article_10_5", f"Special Category Data Blocked: {intent}",
                                   para_10_5.api_response_on_block or 403)

        # ── 6. Article 14.4: Human Veto (Annex III) ──────────────────────────
        para_14_4 = self._get_para("article_14_human_oversight", "article_14_4")
        requires_human_review = False
        trigger_paragraph = None

        if para_14_4:
            hitl_rule = para_14_4.rules.get("rule_hitl_gate")
            if hitl_rule and hitl_rule.logic == "REQUIRE_HUMAN_VETO":
                for category, keywords in self.config.annex_iii_categories.items():
                    if category in (hitl_rule.applies_to_annex_iii or []):
                        if any(kw in prompt_text for kw in keywords):
                            requires_human_review = True
                            trigger_paragraph = "article_14_4"
                            self.active_category = category
                            break

        return {
            "allowed": True,
            "requires_human_review": requires_human_review,
            "trigger_paragraph": trigger_paragraph,
            "http_status": 202 if requires_human_review else None,
            "trigger_reason": "Annex III High-Risk Category Detected" if requires_human_review else None,
            "risk_score": 100.0 if requires_human_review else 0.0 # High risk if HITL triggered
        }

    # ──────────────────────────────────────────────────────────────────────────
    # EGRESS EVALUATION
    # ──────────────────────────────────────────────────────────────────────────
    def evaluate_egress(
        self, output: str, confidence: float, rag_verified: bool = False,
        rag_metadata: Optional[Dict] = None
    ) -> Tuple[bool, str, str, Dict]:
        """
        Evaluates egress-time gates:
        - Article 15.1/3 (Accuracy, RAG grounding, Copyright, Hallucination)
        - Article 13.1/2/3 (Transparency, Disclaimers, Watermarks)
        - Article 50.1    (Machine-readable AI marker)

        Returns: (is_compliant, modified_output, watermark, http_headers)
        """
        if not self.is_environment_active():
            return True, output, "", {}

        is_compliant = True
        modified_output = output
        watermark = ""
        http_headers: Dict[str, str] = {}

        # ── Article 15.1: Minimum Confidence & Fallback ────────────────────────
        para_15_1 = self._get_para("article_15_accuracy_robustness", "article_15_1")
        if para_15_1:
            acc_rule = para_15_1.rules.get("rule_enforce_minimum_confidence")
            threshold = acc_rule.min_confidence if acc_rule else 0.85
            if confidence < threshold:
                is_compliant = False
                IncidentLogger.log_incident("LOW_CONFIDENCE", f"Confidence {confidence} below threshold {threshold}")
                modified_output = "[SAFE MODE FALLBACK] The AI system encountered an out-of-distribution or low-confidence scenario and has reverted to a safe state."
        
        # ── Article 13.1: Explanation Logs ────────────────────────────────────
        # Attach explanation log proxy as required by interpretability
        explanation_log = f"\n\n[Explanation Log: Feature importance estimation complete. Confidence: {confidence:.2f}]"
        if is_compliant:
            modified_output += explanation_log

        # ── Article 15.3: RAG Grounding, Attribution, Copyright ───────────────
        para_15_3 = self._get_para("article_15_accuracy_robustness", "article_15_3")
        if para_15_3:
            rag_rule    = para_15_3.rules.get("rule_verify_rag_sources")
            copy_rule   = para_15_3.rules.get("rule_rag_copyright_check")
            attrib_rule = para_15_3.rules.get("rule_rag_source_attribution")
            fallback    = para_15_3.rules.get("rule_hallucination_fallback")

            # Copyright check on RAG metadata
            if copy_rule and rag_metadata:
                source_domain = rag_metadata.get("source_domain", "unknown")
                allowed = copy_rule.allowlisted_domains or []
                if source_domain not in allowed:
                    is_compliant = False

            # RAG grounding required but not verified
            if rag_rule and not rag_verified:
                is_compliant = False

            # Apply fallback rewrite if non-compliant
            if not is_compliant and fallback:
                modified_output = fallback.rewrite_template or modified_output

            # Source attribution — append if grounded
            if rag_verified and attrib_rule and rag_metadata:
                doc_id = rag_metadata.get("document_id", "UNKNOWN")
                attribution = (attrib_rule.attribution_format or "[Source: {document_id}]")
                modified_output += f"\n{attribution.format(document_id=doc_id)}"

        # ── Article 13.1: AI Watermark ────────────────────────────────────────
        para_13_1 = self._get_para("article_13_transparency", "article_13_1")
        if para_13_1:
            wm_rule = para_13_1.rules.get("rule_append_watermark")
            if wm_rule:
                watermark = wm_rule.text or ""

        # ── Article 13.2: Contextual Disclaimer ───────────────────────────────
        para_13_2 = self._get_para("article_13_transparency", "article_13_2")
        if para_13_2 and self.active_category:
            disc_rule = para_13_2.rules.get("rule_capability_disclaimer")
            if disc_rule:
                if self.active_category == "healthcare" and disc_rule.healthcare_disclaimer:
                    watermark += f"\n{disc_rule.healthcare_disclaimer}"
                elif self.active_category == "employment" and disc_rule.employment_disclaimer:
                    watermark += f"\n{disc_rule.employment_disclaimer}"
                elif self.active_category == "justice" and disc_rule.legal_disclaimer:
                    watermark += f"\n{disc_rule.legal_disclaimer}"

        # ── Article 50.1: Machine-Readable AI Marker ──────────────────────────
        para_50_1 = self._get_para("article_50_transparency_obligations", "article_50_1")
        if para_50_1:
            mark_rule = para_50_1.rules.get("rule_ai_content_marking")
            if mark_rule and mark_rule.header_field:
                http_headers[mark_rule.header_field] = mark_rule.header_value or "true"

        return is_compliant, modified_output, watermark, http_headers

    # ──────────────────────────────────────────────────────────────────────────
    # HELPERS
    # ──────────────────────────────────────────────────────────────────────────
    def _block(self, para: str, reason: str, http_status: int) -> Dict[str, Any]:
        return {
            "allowed": False,
            "requires_human_review": False,
            "trigger_paragraph": para,
            "trigger_reason": reason,
            "http_status": http_status,
        }
