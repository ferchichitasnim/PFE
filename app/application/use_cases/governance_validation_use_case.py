from __future__ import annotations

from dataclasses import dataclass

from app.application.services.governance_service import GovernanceService
from app.domain.entities.governance_status import GovernanceStatus


@dataclass(slots=True)
class GovernanceValidationCommand:
    report_id: int


class GovernanceValidationUseCase:
    def __init__(self, governance_service: GovernanceService) -> None:
        self._governance_service = governance_service

    def execute(self, cmd: GovernanceValidationCommand) -> GovernanceStatus:
        return self._governance_service.validate_for_report(cmd.report_id)

