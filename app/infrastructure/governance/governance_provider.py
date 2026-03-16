from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Tuple

from app.domain.value_objects.governance_rules import CertificationStatus, SensitivityLabel


class GovernanceProvider(ABC):
    """Abstract source of governance metadata for datasets."""

    @abstractmethod
    def get_dataset_governance(self, dataset_id: int) -> Tuple[CertificationStatus, SensitivityLabel]:
        raise NotImplementedError

