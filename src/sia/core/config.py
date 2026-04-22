import yaml
from pydantic import BaseModel
from typing import Any, Optional, Dict, List
from pathlib import Path


class Rule(BaseModel):
    """Atomic governance rule with explicit category classification."""
    model_config = {"extra": "allow"}

    logic: str
    category: str = "runtime_gate"  # runtime_gate | deployment_assertion | governance_doc
    # Blocking / filtering
    on_fail: Optional[str] = None
    on_trigger: Optional[str] = None
    api_response_on_block: Optional[int] = None
    # Domain & practice lists
    domains: Optional[List[str]] = None
    practices: Optional[List[str]] = None
    categories: Optional[List[str]] = None
    patterns: Optional[List[str]] = None
    allowlisted_domains: Optional[List[str]] = None
    # Confidence & quality thresholds
    min_confidence: float = 0.85
    max_acceptable_residual_risk: Optional[str] = None
    alert_threshold_drop: Optional[float] = None
    incident_threshold_confidence: Optional[float] = None
    consecutive_block_alert: Optional[int] = None
    max_tokens: Optional[int] = None
    max_prompt_length: Optional[int] = None
    allowed_encodings: Optional[List[str]] = None
    # Traceability
    rewrite_template: Optional[str] = None
    hash_algorithm: Optional[str] = None
    retention_years: Optional[int] = None
    retention_path: Optional[str] = None
    # Transparency
    text: Optional[str] = None
    position: Optional[str] = None
    header_field: Optional[str] = None
    header_value: Optional[str] = None
    attribution_format: Optional[str] = None
    # HITL
    applies_to_annex_iii: Optional[List[str]] = None
    timeout_seconds: Optional[int] = None
    override_mechanisms: Optional[List[str]] = None
    # Disclaimers
    healthcare_disclaimer: Optional[str] = None
    employment_disclaimer: Optional[str] = None
    legal_disclaimer: Optional[str] = None
    # Metadata validation
    required_fields: Optional[List[str]] = None
    required_metrics: Optional[List[str]] = None
    # Article 9 risk
    annex_iii_check: Optional[bool] = None
    # PII
    pii_types: Optional[List[str]] = None
    fallback_action: Optional[str] = None


class ParagraphConfig(BaseModel):
    description: str
    api_response_on_block: Optional[int] = None
    api_response_on_trigger: Optional[int] = None
    rules: Dict[str, Rule]


class ArticleConfig(BaseModel):
    paragraphs: Dict[str, ParagraphConfig]


class Environments(BaseModel):
    active: List[str]


class EUAIActConfig(BaseModel):
    environments: Environments
    annex_iii_categories: Dict[str, List[str]]
    articles: Dict[str, ArticleConfig]


def load_logic_gates(file_path: str | Path) -> EUAIActConfig:
    with open(file_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return EUAIActConfig(**data)
