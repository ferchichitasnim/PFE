from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(slots=True)
class Report:
    """Domain entity representing a Power BI report."""

    id: Optional[int]
    name: str
    pbix_path: str
    uploaded_at: datetime
    status: str
    dataset_id: Optional[int] = None

