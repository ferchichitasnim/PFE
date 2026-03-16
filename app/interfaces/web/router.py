from __future__ import annotations

import os

from fastapi import APIRouter, BackgroundTasks, File, HTTPException, Request, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.application.use_cases.analyze_report_use_case import AnalyzeReportCommand, AnalyzeReportUseCase
from app.application.use_cases.upload_report_use_case import UploadReportCommand, UploadReportUseCase
from app.core.config import get_settings
from app.domain.repositories.narrative_repository import NarrativeRepository
from app.domain.repositories.report_repository import ReportRepository


def get_web_router(
    templates: Jinja2Templates,
    upload_uc: UploadReportUseCase,
    analyze_uc: AnalyzeReportUseCase,
    report_repo: ReportRepository,
    narrative_repo: NarrativeRepository,
) -> APIRouter:
    router = APIRouter()
    settings = get_settings()

    @router.get("/", response_class=HTMLResponse)
    async def index(request: Request) -> HTMLResponse:
        reports = report_repo.list()
        return templates.TemplateResponse(
            "index.html",
            {"request": request, "reports": reports},
        )

    @router.post("/web/upload")
    async def web_upload(background: BackgroundTasks, file: UploadFile = File(...)) -> RedirectResponse:
        if not file.filename.lower().endswith(".pbix"):
            raise HTTPException(status_code=400, detail="Only .pbix uploads are supported")

        os.makedirs(settings.upload_dir, exist_ok=True)
        dest_path = os.path.join(settings.upload_dir, file.filename)
        content = await file.read()
        with open(dest_path, "wb") as f:
            f.write(content)

        report = upload_uc.execute(UploadReportCommand(pbix_path=dest_path, report_name=file.filename))
        background.add_task(lambda: analyze_uc.execute(AnalyzeReportCommand(report_id=report.id or 0)))

        return RedirectResponse(url=f"/reports/{report.id}", status_code=303)

    @router.post("/web/reports/{report_id}/analyze")
    async def web_analyze(report_id: int) -> RedirectResponse:
        analyze_uc.execute(AnalyzeReportCommand(report_id=report_id))
        return RedirectResponse(url=f"/reports/{report_id}", status_code=303)

    @router.get("/reports/{report_id}", response_class=HTMLResponse)
    async def report_detail(request: Request, report_id: int) -> HTMLResponse:
        report = report_repo.get(report_id)
        narrative = narrative_repo.get_by_report_id(report_id)
        return templates.TemplateResponse(
            "report_detail.html",
            {"request": request, "report": report, "narrative": narrative},
        )

    return router

