from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List

from app.core.logging import get_logger
from app.infrastructure.powerbi_desktop.desktop_dax_client import (
    DesktopDaxClient,
    discover_powerbi_desktop_connection,
)

logger = get_logger(__name__)


@dataclass(slots=True)
class SemanticModel:
    report_id: int
    dataset_id: int
    kpi_definitions: List[str]


@dataclass(slots=True)
class DatasetInfo:
    dataset_id: int
    name: str
    tags: Dict[str, str]


class MCPClient(ABC):
    @abstractmethod
    def get_semantic_model(self, report_id: int) -> SemanticModel:
        raise NotImplementedError

    @abstractmethod
    def get_dataset_info(self, dataset_id: int) -> DatasetInfo:
        raise NotImplementedError

    @abstractmethod
    def get_kpi_series(self, report_id: int) -> Dict[str, List[float]]:
        """Return simple time-series values per KPI name for analysis."""
        raise NotImplementedError


class MockMCPClient(MCPClient):
    """Mock implementation returning deterministic metadata and KPI values."""

    def get_semantic_model(self, report_id: int) -> SemanticModel:
        # For now assume a single dataset per report with same id
        return SemanticModel(
            report_id=report_id,
            dataset_id=report_id,
            kpi_definitions=["Revenue", "Cost", "Profit"],
        )

    def get_dataset_info(self, dataset_id: int) -> DatasetInfo:
        return DatasetInfo(
            dataset_id=dataset_id,
            name=f"Dataset {dataset_id}",
            tags={"domain": "Sales", "region": "Global"},
        )

    def get_kpi_series(self, report_id: int) -> Dict[str, List[float]]:
        # Simple synthetic data: last two periods for each KPI
        base = 100.0 + report_id
        return {
            "Revenue": [base * 0.9, base],  # slight increase
            "Cost": [base * 0.7, base * 0.8],
            "Profit": [base * 0.2, base * 0.25],
        }


class PowerBIDesktopMCPClient(MCPClient):
    """
    Gets real KPI values by querying the local Power BI Desktop model (DAX).
    Falls back to mock behavior if Desktop isn't available.
    """

    def __init__(self, fallback: MCPClient | None = None) -> None:
        self._fallback = fallback or MockMCPClient()

    def _client(self) -> DesktopDaxClient | None:
        info = discover_powerbi_desktop_connection()
        if not info:
            return None
        return DesktopDaxClient(port=info.port)

    def get_semantic_model(self, report_id: int) -> SemanticModel:
        client = self._client()
        if not client:
            return self._fallback.get_semantic_model(report_id)
        try:
            measures = client.list_measures()
            # keep it small for narrative
            measures = measures[:10]
            return SemanticModel(report_id=report_id, dataset_id=report_id, kpi_definitions=measures)
        except Exception as e:
            logger.warning("Desktop semantic model read failed; using fallback", extra={"error": str(e)})
            return self._fallback.get_semantic_model(report_id)

    def get_dataset_info(self, dataset_id: int) -> DatasetInfo:
        # Desktop mode: we don't have a real dataset name easily; use a placeholder
        return DatasetInfo(dataset_id=dataset_id, name=f"DesktopModel {dataset_id}", tags={"source": "PowerBIDesktop"})

    def get_kpi_series(self, report_id: int) -> Dict[str, List[float]]:
        client = self._client()
        if not client:
            return self._fallback.get_kpi_series(report_id)
        try:
            measures = client.list_measures()[:10]
            series: Dict[str, List[float]] = {}
            for m in measures:
                v = client.evaluate_measure(m)
                if v is None:
                    continue
                # No time context available by default; duplicate as previous/current.
                series[m] = [v, v]
            if not series:
                return self._fallback.get_kpi_series(report_id)
            return series
        except Exception as e:
            logger.warning("Desktop KPI read failed; using fallback", extra={"error": str(e)})
            return self._fallback.get_kpi_series(report_id)

