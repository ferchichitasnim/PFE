from __future__ import annotations

from collections import defaultdict
from typing import Any, Callable, DefaultDict, List, Type

from app.core.events import EventBus
from app.core.logging import get_logger


logger = get_logger(__name__)


class InMemoryEventBus(EventBus):
    def __init__(self) -> None:
        self._subscribers: DefaultDict[Type[Any], List[Callable[[Any], None]]] = defaultdict(list)

    def subscribe(self, event_type: Type[Any], handler: Callable[[Any], None]) -> None:
        self._subscribers[event_type].append(handler)
        logger.info("Subscribed handler to event", extra={"event_type": event_type.__name__})

    def publish(self, event: Any) -> None:
        event_cls = type(event)
        handlers = self._subscribers.get(event_cls, [])
        logger.info(
            "Publishing event",
            extra={"event_type": event.event_type, "handlers": len(handlers)},
        )
        for handler in handlers:
            handler(event)

