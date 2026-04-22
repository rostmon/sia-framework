from typing import Any, Dict, Tuple
from sia.core.config import EUAIActConfig

class RuleEvaluationEngine:
    def __init__(self, config: EUAIActConfig, environment: str = "prod"):
        self.config = config
        self.environment = environment

    def is_environment_active(self) -> bool:
        return self.environment in self.config.environments.active

    def evaluate_ingress(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluates Article 10 and Article 14 paragraph rules.
        """
        if not self.is_environment_active():
            return {"allowed": True, "requires_human_review": False, "trigger_paragraph": None}
            
        intent = context.get("intent", "low_risk")
        prompt_text = context.get("prompt_text", "").lower()
        
        requires_human_review = False
        trigger_paragraph = None
        
        # Check Article 14.4
        art_14 = self.config.articles.get("article_14_human_oversight")
        if art_14:
            para_14_4 = art_14.paragraphs.get("article_14_4")
            if para_14_4:
                hitl_rule = para_14_4.rules.get("hitl_gate")
                if hitl_rule and hitl_rule.logic == "REQUIRE_HUMAN_VETO":
                    for category, keywords in self.config.annex_iii_categories.items():
                        if category in hitl_rule.applies_to_annex_iii:
                            if any(kw in prompt_text for kw in keywords):
                                requires_human_review = True
                                trigger_paragraph = "article_14_4"
                                break

        return {
            "allowed": True,
            "requires_human_review": requires_human_review,
            "trigger_paragraph": trigger_paragraph
        }

    def evaluate_egress(self, output: str, confidence: float) -> Tuple[bool, str, str]:
        """
        Evaluates Article 13 and 15 rules on output.
        Returns (is_compliant, modified_output, watermark)
        """
        if not self.is_environment_active():
            return True, output, ""

        is_compliant = True
        modified_output = output
        watermark = ""

        # Article 15.1 and 15.3 Check
        art_15 = self.config.articles.get("article_15_accuracy_robustness")
        if art_15:
            # 15.1 Min Accuracy
            para_15_1 = art_15.paragraphs.get("article_15_1")
            if para_15_1:
                acc_rule = para_15_1.rules.get("min_accuracy")
                if acc_rule and confidence < acc_rule.min_confidence:
                    is_compliant = False
            
            # 15.3 Resilience
            para_15_3 = art_15.paragraphs.get("article_15_3")
            if para_15_3:
                truth_rule = para_15_3.rules.get("truth_razor")
                if truth_rule and truth_rule.logic == "REQUIRE_RAG_GROUNDING" and not is_compliant:
                    if truth_rule.on_fail == "BLOCK_AND_REWRITE":
                        modified_output = truth_rule.rewrite_template

        # Article 13.1 Check
        art_13 = self.config.articles.get("article_13_transparency")
        if art_13:
            para_13_1 = art_13.paragraphs.get("article_13_1")
            if para_13_1:
                wm_rule = para_13_1.rules.get("watermarking")
                if wm_rule and wm_rule.logic == "APPEND_WATERMARK":
                    watermark = wm_rule.text

        return is_compliant, modified_output, watermark
