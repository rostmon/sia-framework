"""
Conformity Assessment Module — Tracks static compliance assertions for Article 43.
"""
from __future__ import annotations
import yaml
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from pydantic import BaseModel


class ConformityRequirement(BaseModel):
    title: str
    description: str
    checks: Dict[str, str]
    status: Dict[str, bool] = {}  # check_id -> completion_status


class ConformityAssessor:
    """
    Manages the lifecycle of a Conformity Assessment.
    Persists progress to logs/conformity_state.json.
    """

    def __init__(self, config_path: str = "configs/conformity_checklist.yaml", state_path: str = "logs/conformity_state.json"):
        self.config_path = Path(config_path)
        self.state_path = Path(state_path)
        self.requirements: Dict[str, ConformityRequirement] = {}
        self._load_config()
        self._load_state()

    def _load_config(self):
        if not self.config_path.exists():
            return
        with open(self.config_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            for req_id, req_data in data.get("requirements", {}).items():
                self.requirements[req_id] = ConformityRequirement(**req_data)

    def _load_state(self):
        if not self.state_path.exists():
            # Initialize empty status
            for req in self.requirements.values():
                req.status = {check_id: False for check_id in req.checks}
            return
        
        with open(self.state_path, "r", encoding="utf-8") as f:
            state = json.load(f)
            for req_id, status in state.items():
                if req_id in self.requirements:
                    self.requirements[req_id].status = status

    def save_state(self):
        state = {req_id: req.status for req_id, req in self.requirements.items()}
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.state_path, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2)

    def update_check(self, req_id: str, check_id: str, completed: bool):
        if req_id in self.requirements and check_id in self.requirements[req_id].status:
            self.requirements[req_id].status[check_id] = completed
            self.save_state()

    def get_progress(self) -> Dict[str, Any]:
        total_checks = 0
        completed_checks = 0
        details = {}

        for req_id, req in self.requirements.items():
            req_total = len(req.checks)
            req_completed = sum(1 for v in req.status.values() if v)
            total_checks += req_total
            completed_checks += req_completed
            details[req_id] = {
                "title": req.title,
                "total": req_total,
                "completed": req_completed,
                "percent": round((req_completed / req_total) * 100) if req_total else 0,
                "checks": req.checks,
                "status": req.status
            }

        return {
            "overall_percent": round((completed_checks / total_checks) * 100) if total_checks else 0,
            "total": total_checks,
            "completed": completed_checks,
            "requirements": details
        }
