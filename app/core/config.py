from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    database_url: str
    ollama_base_url: str
    ollama_model: str
    use_stub_llm: bool
    upload_dir: str
    use_powerbi_desktop_kpis: bool


def get_settings() -> Settings:
    return Settings(
        database_url=os.getenv("DATABASE_URL", "sqlite:///./data.db"),
        ollama_base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        ollama_model=os.getenv("OLLAMA_MODEL", "llama3:latest"),
        use_stub_llm=os.getenv("USE_STUB_LLM", "false").lower() == "true",
        upload_dir=os.getenv("UPLOAD_DIR", "./uploads"),
        use_powerbi_desktop_kpis=os.getenv("USE_POWERBI_DESKTOP_KPIS", "true").lower() == "true",
    )

