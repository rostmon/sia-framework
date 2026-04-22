import yaml
from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Any
from pathlib import Path

class Rule(BaseModel):
    logic: str
    on_fail: Optional[str] = None
    domains: Optional[List[str]] = None
    retention_policy: Optional[str] = None
    text: Optional[str] = None
    applies_to_annex_iii: Optional[List[str]] = None
    on_trigger: Optional[str] = None
    min_confidence: Optional[float] = None
    rewrite_template: Optional[str] = None

class ArticleConfig(BaseModel):
    description: str
    rules: Dict[str, Rule]

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
