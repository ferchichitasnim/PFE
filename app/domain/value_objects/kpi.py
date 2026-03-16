from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class TrendDirection(str, Enum):
    UP = "up"
    DOWN = "down"
    STABLE = "stable"


@dataclass(slots=True)
class KPI:
    """Value object capturing KPI values and movement."""

    name: str
    current_value: float
    previous_value: Optional[float]
    unit: Optional[str]
    delta: Optional[float]
    trend: TrendDirection
    is_anomaly: bool = False

