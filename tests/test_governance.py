from app.domain.value_objects.governance_rules import CertificationStatus, SensitivityLabel, GovernanceDecision
from app.infrastructure.governance.local_rule_engine import evaluate_governance


def test_governance_passes_when_certified_and_allowed_label():
    status = evaluate_governance(CertificationStatus.CERTIFIED, SensitivityLabel.INTERNAL)
    assert status.decision == GovernanceDecision.PASS


def test_governance_blocks_when_not_certified():
    status = evaluate_governance(CertificationStatus.NOT_CERTIFIED, SensitivityLabel.INTERNAL)
    assert status.decision == GovernanceDecision.BLOCKED


def test_governance_blocks_when_highly_confidential():
    status = evaluate_governance(CertificationStatus.CERTIFIED, SensitivityLabel.HIGHLY_CONFIDENTIAL)
    assert status.decision == GovernanceDecision.BLOCKED

