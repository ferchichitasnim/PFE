from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(slots=True)
class NarrativeSummary:
    """Narrative text generated for a report."""

    id: Optional[int]
    report_id: int
    text: str
    created_at: datetime

