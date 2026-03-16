from __future__ import annotations

import json
from typing import Any, Dict, List

from sqlalchemy.orm import Session

from app.domain.repositories.event_repository import EventRepository
from app.infrastructure.database.models import EventModel


class SqlAlchemyEventRepository(EventRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def append(self, event_type: str, payload: Dict[str, Any]) -> None:
        model = EventModel(event_type=event_type, payload=json.dumps(payload))
        self._session.add(model)
        self._session.commit()

    def list(self) -> List[Dict[str, Any]]:
        models = self._session.query(EventModel).all()
        return [
            {"event_type": m.event_type, "payload": json.loads(m.payload), "created_at": m.created_at}
            for m in models
        ]

