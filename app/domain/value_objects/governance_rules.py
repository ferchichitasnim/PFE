from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import List


class CertificationStatus(str, Enum):
    NOT_CERTIFIED = "not_certified"
    CERTIFIED = "certified"


class SensitivityLabel(str, Enum):
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    HIGHLY_CONFIDENTIAL = "highly_confidential"


class GovernanceDecision(str, Enum):
    PASS = "PASS"
    BLOCKED = "BLOCKED"


@dataclass(slots=True)
class GovernanceRuleEvaluation:
    rule_name: str
    passed: bool
    message: str


@dataclass(slots=True)
class GovernanceOutcome:
    decision: GovernanceDecision
    evaluations: List[GovernanceRuleEvaluation]

