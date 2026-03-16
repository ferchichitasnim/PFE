from __future__ import annotations

from app.domain.entities.governance_status import GovernanceStatus
from app.domain.repositories.dataset_repository import DatasetRepository
from app.infrastructure.governance.governance_provider import GovernanceProvider
from app.infrastructure.governance.local_rule_engine import evaluate_governance


class GovernanceService:
    def __init__(
        self,
        dataset_repo: DatasetRepository,
        governance_provider: GovernanceProvider,
    ) -> None:
        self._dataset_repo = dataset_repo
        self._governance_provider = governance_provider

    def validate_for_report(self, report_id: int) -> GovernanceStatus:
        dataset = self._dataset_repo.get_by_report_id(report_id)
        if not dataset:
            # Treat missing dataset as non-compliant
            return evaluate_governance(
                certification=self._governance_provider.get_dataset_governance(report_id)[0],
                sensitivity=self._governance_provider.get_dataset_governance(report_id)[1],
            )

        certification, sensitivity = self._governance_provider.get_dataset_governance(
            dataset.id  # type: ignore[arg-type]
        )
        return evaluate_governance(certification=certification, sensitivity=sensitivity)

