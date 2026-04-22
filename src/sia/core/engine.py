from typing import Any, Dict, Tuple
from sia.core.config import EUAIActConfig

class RuleEvaluationEngine:
    def __init__(self, config: EUAIActConfig, environment: str = "prod"):
        self.config = config
        self.environment = environment
        self.active_category = None  # Store category for egress disclaimers

    def is_environment_active(self) -> bool:
        return self.environment in self.config.environments.active

    def evaluate_ingress(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluates Articles 5, 10, 14, and 15.4 atomic rules.
        """
        if not self.is_environment_active():
            return {"allowed": True, "requires_human_review": False, "trigger_paragraph": None, "trigger_reason": None}
            
        intent = context.get("intent", "low_risk")
        prompt_text = context.get("prompt_text", "").lower()
        self.active_category = None
        
        # 0. Check Article 15.4 (Cybersecurity / Prompt Injection)
        art_15 = self.config.articles.get("article_15_accuracy_robustness")
        if art_15:
             para_15_4 = art_15.paragraphs.get("article_15_4")
             if para_15_4:
                 cyb_rule = para_15_4.rules.get("rule_cybersecurity_defense")
                 if cyb_rule and cyb_rule.logic == "BLOCK_PROMPT_INJECTION":
                     if intent == "prompt_injection":
                         return {"allowed": False, "requires_human_review": False, "trigger_paragraph": "article_15_4", "trigger_reason": "Adversarial Prompt Injection Detected"}

        # 1. Check Article 5 (Prohibited Practices)
        art_5 = self.config.articles.get("article_5_prohibited_practices")
        if art_5:
             para_5_1 = art_5.paragraphs.get("article_5_1")
             if para_5_1:
                 prohib_rule = para_5_1.rules.get("rule_block_prohibited")
                 if prohib_rule and prohib_rule.logic == "BLOCK_PROHIBITED_PRACTICES":
                     if intent in prohib_rule.practices:
                         return {"allowed": False, "requires_human_review": False, "trigger_paragraph": "article_5_1", "trigger_reason": f"Prohibited Practice: {intent}"}

        # 2. Check Article 10.2(f) (Bias / Prohibited Domains)
        art_10 = self.config.articles.get("article_10_data_governance")
        if art_10:
            para_10_2_f = art_10.paragraphs.get("article_10_2_f")
            if para_10_2_f:
                bias_rule = para_10_2_f.rules.get("rule_bias_detection")
                if bias_rule and bias_rule.logic == "BLOCK_PROHIBITED_DOMAINS":
                    if intent in bias_rule.domains:
                        return {"allowed": False, "requires_human_review": False, "trigger_paragraph": "article_10_2_f", "trigger_reason": f"Prohibited Domain: {intent}"}

        # 3. Check Article 14.4 (HITL)
        requires_human_review = False
        trigger_paragraph = None
        
        art_14 = self.config.articles.get("article_14_human_oversight")
        if art_14:
            para_14_4 = art_14.paragraphs.get("article_14_4")
            if para_14_4:
                hitl_rule = para_14_4.rules.get("rule_hitl_gate")
                if hitl_rule and hitl_rule.logic == "REQUIRE_HUMAN_VETO":
                    for category, keywords in self.config.annex_iii_categories.items():
                        if category in hitl_rule.applies_to_annex_iii:
                            if any(kw in prompt_text for kw in keywords):
                                requires_human_review = True
                                trigger_paragraph = "article_14_4"
                                self.active_category = category # Save for Article 13.2
                                break

        return {
            "allowed": True,
            "requires_human_review": requires_human_review,
            "trigger_paragraph": trigger_paragraph,
            "trigger_reason": "Annex III Mapping" if requires_human_review else None
        }

    def evaluate_egress(self, output: str, confidence: float, rag_verified: bool = False) -> Tuple[bool, str, str]:
        """
        Evaluates Article 13 and 15 atomic rules on output.
        Returns (is_compliant, modified_output, watermark)
        """
        if not self.is_environment_active():
            return True, output, ""

        is_compliant = True
        modified_output = output
        watermark = ""

        # Article 15.1 Check (Confidence)
        art_15 = self.config.articles.get("article_15_accuracy_robustness")
        if art_15:
            para_15_1 = art_15.paragraphs.get("article_15_1")
            if para_15_1:
                acc_rule = para_15_1.rules.get("rule_enforce_minimum_confidence")
                if acc_rule and confidence < acc_rule.min_confidence:
                    is_compliant = False
            
            # Article 15.3 Check (RAG Verification & Fallback)
            para_15_3 = art_15.paragraphs.get("article_15_3")
            if para_15_3:
                rag_rule = para_15_3.rules.get("rule_verify_rag_sources")
                fallback_rule = para_15_3.rules.get("rule_hallucination_fallback")
                
                if (rag_rule and rag_rule.logic == "REQUIRE_RAG_GROUNDING" and not rag_verified) or not is_compliant:
                    is_compliant = False
                    if fallback_rule and fallback_rule.logic == "BLOCK_AND_REWRITE":
                        modified_output = fallback_rule.rewrite_template

        # Article 13.1 & 13.2 Check (Transparency & Disclaimers)
        art_13 = self.config.articles.get("article_13_transparency")
        if art_13:
            # 13.1 Watermark
            para_13_1 = art_13.paragraphs.get("article_13_1")
            if para_13_1:
                wm_rule = para_13_1.rules.get("rule_append_watermark")
                if wm_rule and wm_rule.logic == "APPEND_WATERMARK":
                    watermark = wm_rule.text
                    
            # 13.2 Disclaimer
            para_13_2 = art_13.paragraphs.get("article_13_2")
            if para_13_2 and self.active_category == "healthcare":
                disc_rule = para_13_2.rules.get("rule_capability_disclaimer")
                if disc_rule and disc_rule.logic == "APPEND_DISCLAIMER":
                     watermark += f"\n{disc_rule.healthcare_disclaimer}"

        return is_compliant, modified_output, watermark
