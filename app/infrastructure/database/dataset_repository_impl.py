from __future__ import annotations

from typing import Optional

from sqlalchemy.orm import Session

from app.domain.entities.dataset import Dataset
from app.domain.repositories.dataset_repository import DatasetRepository
from app.domain.value_objects.governance_rules import CertificationStatus, SensitivityLabel
from app.infrastructure.database.models import DatasetModel, ReportModel


class SqlAlchemyDatasetRepository(DatasetRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, dataset: Dataset) -> Dataset:
        model = DatasetModel(
            name=dataset.name,
            certification_status=dataset.certification_status.value,
            sensitivity_label=dataset.sensitivity_label.value,
        )
        self._session.add(model)
        self._session.commit()
        self._session.refresh(model)
        dataset.id = model.id
        return dataset

    def get(self, dataset_id: int) -> Optional[Dataset]:
        model = self._session.get(DatasetModel, dataset_id)
        if not model:
            return None
        return Dataset(
            id=model.id,
            name=model.name,
            certification_status=CertificationStatus(model.certification_status),
            sensitivity_label=SensitivityLabel(model.sensitivity_label),
        )

    def get_by_report_id(self, report_id: int) -> Optional[Dataset]:
        report = self._session.get(ReportModel, report_id)
        if not report or report.dataset_id is None:
            return None
        return self.get(report.dataset_id)

    def update(self, dataset: Dataset) -> Dataset:
        model = self._session.get(DatasetModel, dataset.id)
        if not model:
            raise ValueError(f"Dataset with id {dataset.id} not found")
        model.name = dataset.name
        model.certification_status = dataset.certification_status.value
        model.sensitivity_label = dataset.sensitivity_label.value
        self._session.commit()
        return dataset

