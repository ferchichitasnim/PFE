from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from app.core.events import EventBus, ReportUploaded
from app.domain.entities.dataset import Dataset
from app.domain.entities.report import Report
from app.domain.repositories.dataset_repository import DatasetRepository
from app.domain.repositories.report_repository import ReportRepository
from app.domain.value_objects.governance_rules import CertificationStatus, SensitivityLabel
from app.infrastructure.powerbi.pbix_extractor import PBIXExtractor


@dataclass(slots=True)
class UploadReportCommand:
    pbix_path: str
    report_name: Optional[str] = None


class UploadReportUseCase:
    def __init__(
        self,
        report_repo: ReportRepository,
        dataset_repo: DatasetRepository,
        pbix_extractor: PBIXExtractor,
        event_bus: EventBus,
    ) -> None:
        self._report_repo = report_repo
        self._dataset_repo = dataset_repo
        self._pbix_extractor = pbix_extractor
        self._event_bus = event_bus

    def execute(self, cmd: UploadReportCommand) -> Report:
        meta = self._pbix_extractor.extract_metadata(cmd.pbix_path)
        report = Report(
            id=None,
            name=cmd.report_name or meta.file_name,
            pbix_path=cmd.pbix_path,
            uploaded_at=datetime.utcnow(),
            status="uploaded",
            dataset_id=None,
        )
        report = self._report_repo.add(report)

        # Prototype: create a default dataset record per report (can be updated later)
        dataset = Dataset(
            id=None,
            name=f"Dataset for {report.name}",
            certification_status=CertificationStatus.CERTIFIED,
            sensitivity_label=SensitivityLabel.INTERNAL,
        )
        dataset = self._dataset_repo.add(dataset)

        report.dataset_id = dataset.id
        report.status = "dataset_linked"
        report = self._report_repo.update(report)

        self._event_bus.publish(ReportUploaded(report_id=report.id or 0))
        return report

