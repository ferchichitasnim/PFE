from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Optional

from app.domain.entities.report import Report


class ReportRepository(ABC):
    """Abstraction for persisting and querying reports."""

    @abstractmethod
    def add(self, report: Report) -> Report:  # returns report with id
        raise NotImplementedError

    @abstractmethod
    def get(self, report_id: int) -> Optional[Report]:
        raise NotImplementedError

    @abstractmethod
    def list(self) -> List[Report]:
        raise NotImplementedError

    @abstractmethod
    def update(self, report: Report) -> Report:
        raise NotImplementedError

