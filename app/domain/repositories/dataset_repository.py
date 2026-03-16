from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

from app.domain.entities.dataset import Dataset


class DatasetRepository(ABC):
    """Abstraction for persisting and querying datasets."""

    @abstractmethod
    def add(self, dataset: Dataset) -> Dataset:
        raise NotImplementedError

    @abstractmethod
    def get(self, dataset_id: int) -> Optional[Dataset]:
        raise NotImplementedError

    @abstractmethod
    def get_by_report_id(self, report_id: int) -> Optional[Dataset]:
        raise NotImplementedError

    @abstractmethod
    def update(self, dataset: Dataset) -> Dataset:
        raise NotImplementedError

