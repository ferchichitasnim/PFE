from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Optional

from app.domain.entities.narrative_summary import NarrativeSummary


class NarrativeRepository(ABC):
    """Abstraction for persisting generated narratives."""

    @abstractmethod
    def add(self, summary: NarrativeSummary) -> NarrativeSummary:
        raise NotImplementedError

    @abstractmethod
    def get(self, narrative_id: int) -> Optional[NarrativeSummary]:
        raise NotImplementedError

    @abstractmethod
    def get_by_report_id(self, report_id: int) -> Optional[NarrativeSummary]:
        raise NotImplementedError

    @abstractmethod
    def list_for_report(self, report_id: int) -> List[NarrativeSummary]:
        raise NotImplementedError

