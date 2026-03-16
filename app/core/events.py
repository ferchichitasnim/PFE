from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Protocol, Type, TypeVar


@dataclass(slots=True)
class Event:
    event_type: str
    payload: Dict[str, Any]


@dataclass(slots=True)
class ReportUploaded:
    report_id: int
    event_type: str = "ReportUploaded"
    payload: Dict[str, Any] = field(init=False)

    def __post_init__(self) -> None:
        self.payload = {"report_id": self.report_id}


@dataclass(slots=True)
class GovernanceBlocked:
    report_id: int
    reason: str
    event_type: str = "GovernanceBlocked"
    payload: Dict[str, Any] = field(init=False)

    def __post_init__(self) -> None:
        self.payload = {"report_id": self.report_id, "reason": self.reason}


@dataclass(slots=True)
class NarrativeGenerated:
    report_id: int
    narrative_text: str
    event_type: str = "NarrativeGenerated"
    payload: Dict[str, Any] = field(init=False)

    def __post_init__(self) -> None:
        self.payload = {"report_id": self.report_id, "narrative_text": self.narrative_text}


@dataclass(slots=True)
class NarrativePublished:
    report_id: int
    narrative_id: int
    event_type: str = "NarrativePublished"
    payload: Dict[str, Any] = field(init=False)

    def __post_init__(self) -> None:
        self.payload = {"report_id": self.report_id, "narrative_id": self.narrative_id}


E = TypeVar("E")


class EventBus(Protocol):
    def subscribe(self, event_type: Type[E], handler: Callable[[E], None]) -> None:
        ...

    def publish(self, event: Any) -> None:
        ...

