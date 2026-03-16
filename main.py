from __future__ import annotations

import os

from fastapi import FastAPI
from fastapi.templating import Jinja2Templates

from app.application.services.governance_service import GovernanceService
from app.application.services.kpi_analysis_service import KPIAnalysisService
from app.application.services.narrative_generator_service import NarrativeGeneratorService
from app.application.use_cases.analyze_report_use_case import AnalyzeReportUseCase
from app.application.use_cases.governance_validation_use_case import GovernanceValidationUseCase
from app.application.use_cases.publish_narrative_use_case import (
    PublishNarrativeCommand,
    PublishNarrativeUseCase,
)
from app.application.use_cases.upload_report_use_case import UploadReportUseCase
from app.core.config import get_settings
from app.core.logging import configure_logging, get_logger
from app.infrastructure.database.dataset_repository_impl import SqlAlchemyDatasetRepository
from app.infrastructure.database.event_repository_impl import SqlAlchemyEventRepository
from app.infrastructure.database.narrative_repository_impl import SqlAlchemyNarrativeRepository
from app.infrastructure.database.report_repository_impl import SqlAlchemyReportRepository
from app.infrastructure.database.session import SessionLocal, init_db
from app.infrastructure.event_bus.in_memory_event_bus import InMemoryEventBus
from app.infrastructure.governance.local_rule_engine import LocalGovernanceProvider
from app.infrastructure.llm.llm_client import OllamaLLMClient, StubLLMClient
from app.infrastructure.mcp.mcp_client import MockMCPClient, PowerBIDesktopMCPClient
from app.infrastructure.powerbi.pbix_extractor import BasicPBIXExtractor
from app.infrastructure.powerbi.powerbi_client import MockPowerBIClient
from app.interfaces.api.routers import get_router
from app.interfaces.web.router import get_web_router


logger = get_logger(__name__)


def create_app() -> FastAPI:
    configure_logging()
    settings = get_settings()
    os.makedirs(settings.upload_dir, exist_ok=True)

    init_db()
    session = SessionLocal()

    # repositories
    report_repo = SqlAlchemyReportRepository(session=session)
    dataset_repo = SqlAlchemyDatasetRepository(session=session)
    narrative_repo = SqlAlchemyNarrativeRepository(session=session)
    _event_repo = SqlAlchemyEventRepository(session=session)

    # infra services
    mcp_client = PowerBIDesktopMCPClient() if settings.use_powerbi_desktop_kpis else MockMCPClient()
    governance_provider = LocalGovernanceProvider(dataset_repo=dataset_repo)
    governance_service = GovernanceService(dataset_repo=dataset_repo, governance_provider=governance_provider)

    llm_client = StubLLMClient() if settings.use_stub_llm else OllamaLLMClient()
    narrative_generator = NarrativeGeneratorService(llm_client=llm_client)
    kpi_analysis = KPIAnalysisService()

    event_bus = InMemoryEventBus()

    # use cases
    governance_uc = GovernanceValidationUseCase(governance_service=governance_service)
    publish_uc = PublishNarrativeUseCase(
        narrative_repo=narrative_repo,
        powerbi_client=MockPowerBIClient(),
        event_bus=event_bus,
    )
    analyze_uc = AnalyzeReportUseCase(
        report_repo=report_repo,
        dataset_repo=dataset_repo,
        mcp_client=mcp_client,
        governance_uc=governance_uc,
        kpi_analysis=kpi_analysis,
        narrative_generator=narrative_generator,
        event_bus=event_bus,
    )
    upload_uc = UploadReportUseCase(
        report_repo=report_repo,
        dataset_repo=dataset_repo,
        pbix_extractor=BasicPBIXExtractor(),
        event_bus=event_bus,
    )

    # event handlers
    from app.core.events import NarrativeGenerated

    event_bus.subscribe(
        NarrativeGenerated,
        lambda e: publish_uc.execute(
            cmd=PublishNarrativeCommand(report_id=e.report_id, narrative_text=e.narrative_text)
        ),
    )

    app = FastAPI(title="PowerBI Storytelling")
    templates = Jinja2Templates(directory="templates")

    app.include_router(
        get_router(
            upload_uc=upload_uc,
            analyze_uc=analyze_uc,
            report_repo=report_repo,
            narrative_repo=narrative_repo,
        )
    )
    app.include_router(
        get_web_router(
            templates=templates,
            upload_uc=upload_uc,
            analyze_uc=analyze_uc,
            report_repo=report_repo,
            narrative_repo=narrative_repo,
        )
    )

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

