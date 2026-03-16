from app.domain.value_objects.kpi import KPI, TrendDirection
from app.infrastructure.llm.llm_client import StubLLMClient


def test_stub_llm_includes_kpi_names():
    client = StubLLMClient()
    kpis = [
        KPI(
            name="Revenue",
            current_value=120.0,
            previous_value=100.0,
            unit=None,
            delta=20.0,
            trend=TrendDirection.UP,
            is_anomaly=True,
        )
    ]
    text = client.generate_narrative(kpis=kpis, metadata={"report_name": "R"})
    assert "Revenue" in text

