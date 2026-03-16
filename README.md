# Storytelling-agent (Power BI Narrative Prototype)

Clean-architecture Python backend that uploads a `.pbix`, runs a governance check, analyzes mock KPIs, generates a narrative (Ollama), and exposes results via FastAPI + a minimal web UI.

## Requirements

- Windows
- Python 3.11+
- (For real narratives) Ollama installed and running

## Setup (PowerShell)

```powershell
cd C:\Users\tasnim.ferchichi_ama\Desktop\work\Storytelling-agent
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Run

```powershell
.\.venv\Scripts\Activate.ps1
python main.py
```

Open:
- Web UI: `http://127.0.0.1:8000/`
- API docs: `http://127.0.0.1:8000/docs`

## What to expect

1. Upload any file with a `.pbix` extension from the home page.
2. The backend stores the report in SQLite (`data.db`) and triggers analysis.
3. If governance passes, a narrative summary is generated and shown on the report page.

## Ollama notes

Defaults:
- `OLLAMA_BASE_URL=http://localhost:11434`
- `OLLAMA_MODEL=llama3:latest`
- `USE_POWERBI_DESKTOP_KPIS=true` (tries to read real KPIs from Power BI Desktop local model)

You can switch the app to a deterministic stub (no Ollama call) with:

```powershell
$env:USE_STUB_LLM="true"
python main.py
```

If Power BI Desktop is not open (or the local model can't be reached), the app falls back to mock KPI data.

## Tests

```powershell
.\.venv\Scripts\Activate.ps1
pytest -q
```

