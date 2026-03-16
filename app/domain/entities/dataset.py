from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from app.domain.value_objects.governance_rules import CertificationStatus, SensitivityLabel


@dataclass(slots=True)
class Dataset:
    """Domain entity representing a dataset backing a report."""

    id: Optional[int]
    name: str
    certification_status: CertificationStatus
    sensitivity_label: SensitivityLabel

