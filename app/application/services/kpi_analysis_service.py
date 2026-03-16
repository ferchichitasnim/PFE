from __future__ import annotations

from typing import Dict, List

from app.domain.value_objects.kpi import KPI, TrendDirection


class KPIAnalysisService:
    def analyze(self, series_by_kpi: Dict[str, List[float]]) -> List[KPI]:
        kpis: List[KPI] = []
        for name, values in series_by_kpi.items():
            if len(values) < 2:
                continue
            previous, current = values[-2], values[-1]
            delta = current - previous
            if abs(delta) < 1e-6:
                trend = TrendDirection.STABLE
            elif delta > 0:
                trend = TrendDirection.UP
            else:
                trend = TrendDirection.DOWN

            # Mark anomaly if change > 15% magnitude
            pct_change = abs(delta) / previous if previous else 0.0
            is_anomaly = pct_change >= 0.15

            kpis.append(
                KPI(
                    name=name,
                    current_value=current,
                    previous_value=previous,
                    unit=None,
                    delta=delta,
                    trend=trend,
                    is_anomaly=is_anomaly,
                )
            )
        return kpis

