from typing import Any, Dict, List, Tuple
from sia.core.config import EUAIActConfig

class RuleEvaluationEngine:
    def __init__(self, config: EUAIActConfig, environment: str = "prod"):
        self.config = config
        self.environment = environment

    def is_environment_active(self) -> bool:
        return self.environment in self.config.environments.active

    def evaluate_ingress(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluates Article 10 and Article 14 rules during pre-processing.
        """
        if not self.is_environment_active():
            return {"allowed": True, "requires_human_review": False}
            
        intent = context.get("intent", "low_risk")
        prompt_text = context.get("prompt_text", "").lower()
        
        # Article 14 HITL Check
        art_14 = self.config.articles.get("article_14_human_oversight")
        requires_human_review = False
        
        if art_14:
            hitl_rule = art_14.rules.get("hitl_gate")
            if hitl_rule and hitl_rule.logic == "REQUIRE_HUMAN_VETO":
                # Check if intent matches Annex III mapping
                for category, keywords in self.config.annex_iii_categories.items():
                    if category in hitl_rule.applies_to_annex_iii:
                        if any(kw in prompt_text for kw in keywords):
                            requires_human_review = True
                            break

        return {
            "allowed": True, # For now we don't block, we just flag for hitl
            "requires_human_review": requires_human_review
        }

    def evaluate_egress(self, output: str, confidence: float) -> Tuple[bool, str, str]:
        """
        Evaluates Article 13 and 15 rules on output.
        Returns (is_compliant, modified_output, watermark)
        """
        if not self.is_environment_active():
            return True, output, ""

        # Article 15 Check
        art_15 = self.config.articles.get("article_15_accuracy_robustness")
        is_compliant = True
        modified_output = output
        
        if art_15:
            truth_rule = art_15.rules.get("truth_razor")
            if truth_rule and truth_rule.logic == "REQUIRE_RAG_GROUNDING":
                if confidence < truth_rule.min_confidence:
                    is_compliant = False
                    if truth_rule.on_fail == "BLOCK_AND_REWRITE":
                        modified_output = truth_rule.rewrite_template

        # Article 13 Check
        art_13 = self.config.articles.get("article_13_transparency")
        watermark = ""
        if art_13:
            wm_rule = art_13.rules.get("watermarking")
            if wm_rule and wm_rule.logic == "APPEND_WATERMARK":
                watermark = wm_rule.text

        return is_compliant, modified_output, watermark
