from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from app.core.events import EventBus, NarrativePublished
from app.domain.entities.narrative_summary import NarrativeSummary
from app.domain.repositories.narrative_repository import NarrativeRepository
from app.infrastructure.powerbi.powerbi_client import PowerBIClient


@dataclass(slots=True)
class PublishNarrativeCommand:
    report_id: int
    narrative_text: str


class PublishNarrativeUseCase:
    def __init__(
        self,
        narrative_repo: NarrativeRepository,
        powerbi_client: PowerBIClient,
        event_bus: EventBus,
    ) -> None:
        self._narrative_repo = narrative_repo
        self._powerbi_client = powerbi_client
        self._event_bus = event_bus

    def execute(self, cmd: PublishNarrativeCommand) -> NarrativeSummary:
        summary = NarrativeSummary(
            id=None,
            report_id=cmd.report_id,
            text=cmd.narrative_text,
            created_at=datetime.utcnow(),
        )
        summary = self._narrative_repo.add(summary)
        self._powerbi_client.insert_narrative(cmd.report_id, cmd.narrative_text)

        self._event_bus.publish(
            NarrativePublished(report_id=cmd.report_id, narrative_id=summary.id or 0)
        )
        return summary

