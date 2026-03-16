from __future__ import annotations

import os
from dataclasses import asdict
from typing import Callable, List

from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, UploadFile

from app.application.use_cases.analyze_report_use_case import AnalyzeReportCommand, AnalyzeReportUseCase
from app.application.use_cases.upload_report_use_case import UploadReportCommand, UploadReportUseCase
from app.core.config import get_settings
from app.domain.repositories.narrative_repository import NarrativeRepository
from app.domain.repositories.report_repository import ReportRepository
from app.interfaces.schemas.report_schemas import (
    AnalyzeReportResponse,
    NarrativeOut,
    ReportOut,
    UploadReportResponse,
)


def get_router(
    upload_uc: UploadReportUseCase,
    analyze_uc: AnalyzeReportUseCase,
    report_repo: ReportRepository,
    narrative_repo: NarrativeRepository,
) -> APIRouter:
    router = APIRouter()
    settings = get_settings()

    @router.post("/reports/upload", response_model=UploadReportResponse)
    async def upload_report(
        background: BackgroundTasks,
        file: UploadFile = File(...),
    ) -> UploadReportResponse:
        if not file.filename.lower().endswith(".pbix"):
            raise HTTPException(status_code=400, detail="Only .pbix uploads are supported")

        os.makedirs(settings.upload_dir, exist_ok=True)
        dest_path = os.path.join(settings.upload_dir, file.filename)
        content = await file.read()
        with open(dest_path, "wb") as f:
            f.write(content)

        report = upload_uc.execute(UploadReportCommand(pbix_path=dest_path, report_name=file.filename))

        # Run analysis in background to keep upload snappy
        background.add_task(lambda: analyze_uc.execute(AnalyzeReportCommand(report_id=report.id or 0)))

        return UploadReportResponse(report=ReportOut(**asdict(report)))  # type: ignore[arg-type]

    @router.post("/reports/{report_id}/analyze", response_model=AnalyzeReportResponse)
    async def analyze_report(report_id: int) -> AnalyzeReportResponse:
        result = analyze_uc.execute(AnalyzeReportCommand(report_id=report_id))
        return AnalyzeReportResponse(
            report_id=report_id,
            governance_decision=result.governance.decision.value,
            governance_reason=result.governance.reason,
            narrative_text=result.narrative_text,
        )

    @router.get("/reports/{report_id}/summary", response_model=NarrativeOut)
    async def get_summary(report_id: int) -> NarrativeOut:
        summary = narrative_repo.get_by_report_id(report_id=report_id)
        if not summary:
            raise HTTPException(status_code=404, detail="No narrative found")
        return NarrativeOut(**asdict(summary))  # type: ignore[arg-type]

    @router.get("/reports", response_model=List[ReportOut])
    async def list_reports() -> List[ReportOut]:
        reports = report_repo.list()
        return [ReportOut(**asdict(r)) for r in reports]  # type: ignore[arg-type]

    return router

