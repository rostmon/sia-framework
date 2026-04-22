"""
Sovereign Systemic Integrity Architecture (SIA)
EU AI Act Governance-as-Code Framework.
"""
from sia.adapters.client import SIAClient, SIAResponse, governed
from sia.adapters.base import ModelAdapter, ModelResponse
from sia.core.engine import RuleEvaluationEngine

__version__ = "0.1.0"
__all__ = [
    "SIAClient",
    "SIAResponse",
    "governed",
    "ModelAdapter",
    "ModelResponse",
    "RuleEvaluationEngine",
]
