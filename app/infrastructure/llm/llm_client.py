from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, Iterable, List

import httpx

from app.core.config import get_settings
from app.core.logging import get_logger
from app.domain.value_objects.kpi import KPI


logger = get_logger(__name__)


class NarrativeLLMClient(ABC):
    @abstractmethod
    def generate_narrative(
        self, kpis: Iterable[KPI], metadata: Dict[str, Any]
    ) -> str:
        raise NotImplementedError


class StubLLMClient(NarrativeLLMClient):
    def generate_narrative(
        self, kpis: Iterable[KPI], metadata: Dict[str, Any]
    ) -> str:
        parts: List[str] = []
        for kpi in kpis:
            direction = kpi.trend.value
            parts.append(f"{kpi.name} is {direction} to {kpi.current_value:.2f}.")
        if not parts:
            return "No KPIs available for analysis."
        return " ".join(parts)


class OllamaLLMClient(NarrativeLLMClient):
    def __init__(self) -> None:
        settings = get_settings()
        self._base_url = settings.ollama_base_url.rstrip("/")
        self._model = settings.ollama_model

    def generate_narrative(
        self, kpis: Iterable[KPI], metadata: Dict[str, Any]
    ) -> str:
        kpi_descriptions = []
        for kpi in kpis:
            kpi_descriptions.append(
                f"- {kpi.name}: current={kpi.current_value:.2f}, "
                f"previous={kpi.previous_value}, trend={kpi.trend.value}, "
                f"anomaly={kpi.is_anomaly}"
            )
        kpi_text = "\n".join(kpi_descriptions) or "No KPIs."

        system_prompt = (
            "You are an analytics assistant that writes concise, business-ready narrative "
            "summaries of KPI performance for Power BI reports."
        )
        user_prompt = (
            f"Report name: {metadata.get('report_name', 'Unknown')}\n"
            f"Dataset: {metadata.get('dataset_name', 'Unknown')}\n"
            f"KPI details:\n{kpi_text}\n\n"
            "Write a short narrative (2-4 sentences) explaining the key changes, trends, "
            "and any anomalies in plain business language."
        )

        payload = {
            "model": self._model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "stream": False,
        }

        url = f"{self._base_url}/api/chat"
        logger.info("Calling Ollama LLM", extra={"url": url, "model": self._model})
        with httpx.Client(timeout=60.0) as client:
            resp = client.post(url, json=payload)
            resp.raise_for_status()
            data = resp.json()

        # Ollama chat response format: choices[0].message.content or similar
        message = data.get("message") or data.get("choices", [{}])[0].get("message")
        if isinstance(message, dict):
            return message.get("content", "").strip()
        # fallback for different formats
        return str(data).strip()

