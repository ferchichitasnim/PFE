from __future__ import annotations

from typing import List, Optional

from sqlalchemy.orm import Session

from app.domain.entities.report import Report
from app.domain.repositories.report_repository import ReportRepository
from app.infrastructure.database.models import ReportModel


class SqlAlchemyReportRepository(ReportRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, report: Report) -> Report:
        model = ReportModel(
            name=report.name,
            pbix_path=report.pbix_path,
            uploaded_at=report.uploaded_at,
            status=report.status,
            dataset_id=report.dataset_id,
        )
        self._session.add(model)
        self._session.commit()
        self._session.refresh(model)
        report.id = model.id
        return report

    def get(self, report_id: int) -> Optional[Report]:
        model = self._session.get(ReportModel, report_id)
        if not model:
            return None
        return Report(
            id=model.id,
            name=model.name,
            pbix_path=model.pbix_path,
            uploaded_at=model.uploaded_at,
            status=model.status,
            dataset_id=model.dataset_id,
        )

    def list(self) -> List[Report]:
        models = self._session.query(ReportModel).all()
        return [
            Report(
                id=m.id,
                name=m.name,
                pbix_path=m.pbix_path,
                uploaded_at=m.uploaded_at,
                status=m.status,
                dataset_id=m.dataset_id,
            )
            for m in models
        ]

    def update(self, report: Report) -> Report:
        model = self._session.get(ReportModel, report.id)
        if not model:
            raise ValueError(f"Report with id {report.id} not found")
        model.name = report.name
        model.pbix_path = report.pbix_path
        model.uploaded_at = report.uploaded_at
        model.status = report.status
        model.dataset_id = report.dataset_id
        self._session.commit()
        return report

