from __future__ import annotations

from typing import Tuple

from app.domain.entities.governance_status import GovernanceStatus
from app.domain.value_objects.governance_rules import (
    CertificationStatus,
    GovernanceDecision,
    GovernanceOutcome,
    GovernanceRuleEvaluation,
    SensitivityLabel,
)
from app.domain.repositories.dataset_repository import DatasetRepository
from app.infrastructure.governance.governance_provider import GovernanceProvider


class LocalGovernanceProvider(GovernanceProvider):
    """Simple governance provider using dataset records."""

    def __init__(self, dataset_repo: DatasetRepository) -> None:
        self._dataset_repo = dataset_repo

    def get_dataset_governance(self, dataset_id: int) -> Tuple[CertificationStatus, SensitivityLabel]:
        dataset = self._dataset_repo.get(dataset_id)
        if not dataset:
            # Default to conservative
            return CertificationStatus.NOT_CERTIFIED, SensitivityLabel.HIGHLY_CONFIDENTIAL
        return dataset.certification_status, dataset.sensitivity_label


def evaluate_governance(
    certification: CertificationStatus, sensitivity: SensitivityLabel
) -> GovernanceStatus:
    evaluations = []

    # Rule 1: dataset must be certified
    rule1_passed = certification == CertificationStatus.CERTIFIED
    evaluations.append(
        GovernanceRuleEvaluation(
            rule_name="dataset_must_be_certified",
            passed=rule1_passed,
            message="Dataset is certified" if rule1_passed else "Dataset is not certified",
        )
    )

    # Rule 2: sensitivity label must allow publication (block highest level)
    allowed_labels = {SensitivityLabel.PUBLIC, SensitivityLabel.INTERNAL, SensitivityLabel.CONFIDENTIAL}
    rule2_passed = sensitivity in allowed_labels
    evaluations.append(
        GovernanceRuleEvaluation(
            rule_name="sensitivity_must_allow_publication",
            passed=rule2_passed,
            message=f"Sensitivity label {sensitivity.value} allows publication"
            if rule2_passed
            else f"Sensitivity label {sensitivity.value} blocks publication",
        )
    )

    decision = (
        GovernanceDecision.PASS
        if all(ev.passed for ev in evaluations)
        else GovernanceDecision.BLOCKED
    )
    outcome = GovernanceOutcome(decision=decision, evaluations=evaluations)
    reason = "; ".join(ev.message for ev in evaluations if not ev.passed) or "All governance checks passed"

    return GovernanceStatus(decision=outcome.decision, reason=reason, evaluations=evaluations)

