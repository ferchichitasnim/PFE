import os
from fastapi.testclient import TestClient


def test_upload_analyze_and_summary_with_stub_llm(tmp_path, monkeypatch):
    monkeypatch.setenv("USE_STUB_LLM", "true")
    # Ensure uploads go to temp dir for test isolation
    monkeypatch.setenv("UPLOAD_DIR", str(tmp_path / "uploads"))
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{tmp_path / 'test.db'}")

    from main import create_app

    app = create_app()
    client = TestClient(app)

    pbix_path = tmp_path / "demo.pbix"
    pbix_path.write_bytes(b"fake pbix")

    with open(pbix_path, "rb") as f:
        resp = client.post("/reports/upload", files={"file": ("demo.pbix", f, "application/octet-stream")})
    assert resp.status_code == 200
    report_id = resp.json()["report"]["id"]

    resp2 = client.post(f"/reports/{report_id}/analyze")
    assert resp2.status_code == 200
    assert resp2.json()["governance_decision"] in ("PASS", "BLOCKED")

    # Narrative is published via event handler when PASS; if blocked, summary may not exist
    if resp2.json()["governance_decision"] == "PASS":
        resp3 = client.get(f"/reports/{report_id}/summary")
        assert resp3.status_code == 200
        assert "text" in resp3.json()

