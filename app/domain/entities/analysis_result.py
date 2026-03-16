from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import List

from app.domain.entities.governance_status import GovernanceStatus
from app.domain.value_objects.kpi import KPI


@dataclass(slots=True)
class AnalysisResult:
    """Captures KPI analysis and governance outcome for a report at a point in time."""

    report_id: int
    generated_at: datetime
    kpis: List[KPI]
    governance_status: GovernanceStatus

