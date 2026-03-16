from __future__ import annotations

from dataclasses import dataclass
from typing import List

from app.domain.value_objects.governance_rules import GovernanceDecision, GovernanceRuleEvaluation


@dataclass(slots=True)
class GovernanceStatus:
    """Represents the overall governance outcome for a dataset/report."""

    decision: GovernanceDecision
    reason: str
    evaluations: List[GovernanceRuleEvaluation]

