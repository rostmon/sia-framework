import yaml
from pydantic import BaseModel, Field
from typing import Optional, Dict
from pathlib import Path

class GovernanceRule(BaseModel):
    """
    Represents a single rule within the Governance-as-Code logic gate.
    """
    logic: Optional[str] = None
    on_fail: Optional[str] = None
    context_match: Optional[str] = None
    requirement: Optional[str] = None
    description: Optional[str] = None

class LogicGateConfig(BaseModel):
    """
    Represents the full YAML configuration for logic gates.
    """
    rules: Dict[str, GovernanceRule]

def load_logic_gates(file_path: str | Path) -> LogicGateConfig:
    """
    Loads and validates the Governance YAML configuration using Pydantic.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    
    if not data:
        return LogicGateConfig(rules={})
        
    return LogicGateConfig(rules={k: GovernanceRule(**v) for k, v in data.items()})
