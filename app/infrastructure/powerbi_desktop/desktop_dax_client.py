from __future__ import annotations

import glob
import os
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple

from app.core.logging import get_logger


logger = get_logger(__name__)


@dataclass(slots=True)
class DesktopConnectionInfo:
    port: int
    workspace_dir: str


def _latest_port_file() -> Optional[str]:
    local_app_data = os.environ.get("LOCALAPPDATA")
    if not local_app_data:
        return None

    base = Path(local_app_data) / "Microsoft" / "Power BI Desktop" / "AnalysisServicesWorkspaces"
    if not base.exists():
        return None

    candidates = list(base.glob("**/msmdsrv.port.txt"))
    if not candidates:
        return None

    candidates.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return str(candidates[0])


def discover_powerbi_desktop_connection() -> Optional[DesktopConnectionInfo]:
    port_file = _latest_port_file()
    if not port_file:
        return None

    try:
        content = Path(port_file).read_text(encoding="utf-8").strip()
        port = int(content)
        return DesktopConnectionInfo(port=port, workspace_dir=str(Path(port_file).parent))
    except Exception as e:
        logger.warning("Failed to read Power BI Desktop port file", extra={"error": str(e)})
        return None


class DesktopDaxClient:
    """
    Connects to the local Analysis Services instance started by Power BI Desktop.
    Requires Power BI Desktop to be open with a PBIX loaded.
    """

    def __init__(self, port: int) -> None:
        self._port = port

    def _conn_str(self) -> str:
        # Power BI Desktop local model is typically exposed as an MSOLAP endpoint
        return f"Provider=MSOLAP;Data Source=localhost:{self._port};Initial Catalog=Model;"

    def list_measures(self) -> List[str]:
        from pyadomd import Pyadomd

        query = "SELECT [Name] FROM $SYSTEM.TMSCHEMA_MEASURES"
        names: List[str] = []
        with Pyadomd(self._conn_str()) as conn:
            conn.open()
            with conn.cursor().execute(query) as cur:
                for row in cur.fetchall():
                    # row can be tuple-like
                    names.append(str(row[0]))
        return names

    def evaluate_measure(self, measure_name: str) -> Optional[float]:
        from pyadomd import Pyadomd

        # DAX: evaluate one scalar measure as a row
        dax = f'EVALUATE ROW("value", [{measure_name}])'
        with Pyadomd(self._conn_str()) as conn:
            conn.open()
            with conn.cursor().execute(dax) as cur:
                rows = cur.fetchall()
        if not rows:
            return None
        val = rows[0][0]
        try:
            return float(val)
        except Exception:
            return None

