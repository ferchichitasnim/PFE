from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List


class EventRepository(ABC):
    """Optional persistence for emitted domain/integration events."""

    @abstractmethod
    def append(self, event_type: str, payload: Dict[str, Any]) -> None:
        raise NotImplementedError

    @abstractmethod
    def list(self) -> List[Dict[str, Any]]:
        raise NotImplementedError

