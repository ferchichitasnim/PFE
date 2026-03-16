from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ReportOut(BaseModel):
    id: int
    name: str
    pbix_path: str
    uploaded_at: datetime
    status: str
    dataset_id: Optional[int] = None


class UploadReportResponse(BaseModel):
    report: ReportOut


class AnalyzeReportResponse(BaseModel):
    report_id: int
    governance_decision: str
    governance_reason: str
    narrative_text: Optional[str] = None


class NarrativeOut(BaseModel):
    id: int
    report_id: int
    text: str
    created_at: datetime

