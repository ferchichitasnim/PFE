from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Session

from app.domain.entities.narrative_summary import NarrativeSummary
from app.domain.repositories.narrative_repository import NarrativeRepository
from app.infrastructure.database.models import NarrativeModel


class SqlAlchemyNarrativeRepository(NarrativeRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, summary: NarrativeSummary) -> NarrativeSummary:
        model = NarrativeModel(
            report_id=summary.report_id,
            text=summary.text,
            created_at=summary.created_at or datetime.utcnow(),
        )
        self._session.add(model)
        self._session.commit()
        self._session.refresh(model)
        summary.id = model.id
        summary.created_at = model.created_at
        return summary

    def get(self, narrative_id: int) -> Optional[NarrativeSummary]:
        model = self._session.get(NarrativeModel, narrative_id)
        if not model:
            return None
        return NarrativeSummary(
            id=model.id,
            report_id=model.report_id,
            text=model.text,
            created_at=model.created_at,
        )

    def get_by_report_id(self, report_id: int) -> Optional[NarrativeSummary]:
        model = (
            self._session.query(NarrativeModel)
            .filter(NarrativeModel.report_id == report_id)
            .order_by(NarrativeModel.created_at.desc())
            .first()
        )
        if not model:
            return None
        return NarrativeSummary(
            id=model.id,
            report_id=model.report_id,
            text=model.text,
            created_at=model.created_at,
        )

    def list_for_report(self, report_id: int) -> List[NarrativeSummary]:
        models = (
            self._session.query(NarrativeModel)
            .filter(NarrativeModel.report_id == report_id)
            .order_by(NarrativeModel.created_at.desc())
            .all()
        )
        return [
            NarrativeSummary(
                id=m.id,
                report_id=m.report_id,
                text=m.text,
                created_at=m.created_at,
            )
            for m in models
        ]

