from __future__ import annotations

from typing import Any, Dict, Iterable

from app.domain.value_objects.kpi import KPI
from app.infrastructure.llm.llm_client import NarrativeLLMClient


class NarrativeGeneratorService:
    def __init__(self, llm_client: NarrativeLLMClient) -> None:
        self._llm_client = llm_client

    def generate(self, kpis: Iterable[KPI], metadata: Dict[str, Any]) -> str:
        return self._llm_client.generate_narrative(kpis=kpis, metadata=metadata)

