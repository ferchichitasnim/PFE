from __future__ import annotations

from abc import ABC, abstractmethod

from app.core.logging import get_logger


logger = get_logger(__name__)


class PowerBIClient(ABC):
    @abstractmethod
    def insert_narrative(self, report_id: int, narrative_text: str) -> None:
        raise NotImplementedError


class MockPowerBIClient(PowerBIClient):
    def insert_narrative(self, report_id: int, narrative_text: str) -> None:
        # Prototype: simulated insertion only
        logger.info(
            "Simulated narrative insert into Power BI",
            extra={"report_id": report_id, "text_len": len(narrative_text)},
        )

