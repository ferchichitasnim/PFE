from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Optional

from app.application.services.kpi_analysis_service import KPIAnalysisService
from app.application.services.narrative_generator_service import NarrativeGeneratorService
from app.application.use_cases.governance_validation_use_case import (
    GovernanceValidationCommand,
    GovernanceValidationUseCase,
)
from app.core.events import EventBus, GovernanceBlocked, NarrativeGenerated
from app.domain.entities.analysis_result import AnalysisResult
from app.domain.entities.governance_status import GovernanceStatus
from app.domain.repositories.dataset_repository import DatasetRepository
from app.domain.repositories.report_repository import ReportRepository
from app.domain.value_objects.governance_rules import GovernanceDecision
from app.infrastructure.mcp.mcp_client import MCPClient


@dataclass(slots=True)
class AnalyzeReportCommand:
    report_id: int


@dataclass(slots=True)
class AnalyzeReportResult:
    governance: GovernanceStatus
    narrative_text: Optional[str]
    analysis: Optional[AnalysisResult]


class AnalyzeReportUseCase:
    def __init__(
        self,
        report_repo: ReportRepository,
        dataset_repo: DatasetRepository,
        mcp_client: MCPClient,
        governance_uc: GovernanceValidationUseCase,
        kpi_analysis: KPIAnalysisService,
        narrative_generator: NarrativeGeneratorService,
        event_bus: EventBus,
    ) -> None:
        self._report_repo = report_repo
        self._dataset_repo = dataset_repo
        self._mcp_client = mcp_client
        self._governance_uc = governance_uc
        self._kpi_analysis = kpi_analysis
        self._narrative_generator = narrative_generator
        self._event_bus = event_bus

    def execute(self, cmd: AnalyzeReportCommand) -> AnalyzeReportResult:
        report = self._report_repo.get(cmd.report_id)
        if not report:
            raise ValueError(f"Report {cmd.report_id} not found")
        dataset = (
            self._dataset_repo.get(report.dataset_id) if report.dataset_id is not None else None
        )

        semantic = self._mcp_client.get_semantic_model(report_id=cmd.report_id)
        dataset_info = self._mcp_client.get_dataset_info(dataset_id=semantic.dataset_id)
        series = self._mcp_client.get_kpi_series(report_id=cmd.report_id)

        governance = self._governance_uc.execute(GovernanceValidationCommand(report_id=cmd.report_id))
        if governance.decision == GovernanceDecision.BLOCKED:
            self._event_bus.publish(GovernanceBlocked(report_id=cmd.report_id, reason=governance.reason))
            report.status = "governance_blocked"
            self._report_repo.update(report)
            return AnalyzeReportResult(governance=governance, narrative_text=None, analysis=None)

        kpis = self._kpi_analysis.analyze(series_by_kpi=series)
        metadata: Dict[str, Any] = {
            "report_name": report.name,
            "dataset_name": dataset.name if dataset else dataset_info.name,
            "tags": dataset_info.tags,
            "kpis": semantic.kpi_definitions,
        }

        narrative = self._narrative_generator.generate(kpis=kpis, metadata=metadata)
        analysis = AnalysisResult(
            report_id=cmd.report_id,
            generated_at=datetime.utcnow(),
            kpis=kpis,
            governance_status=governance,
        )

        report.status = "narrative_generated"
        self._report_repo.update(report)
        self._event_bus.publish(NarrativeGenerated(report_id=cmd.report_id, narrative_text=narrative))

        return AnalyzeReportResult(governance=governance, narrative_text=narrative, analysis=analysis)

