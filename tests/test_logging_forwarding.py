import sys
from pathlib import Path as _Path
import importlib.util

root_path = _Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root_path))

import requests
import httpx
from fastapi.testclient import TestClient

from incident_manager.app.main import app as incident_app

# Dynamically load the sentinelcore-ai module since the directory name has a dash
sentinel_dir = root_path / "sentinelcore-ai"
sys.path.insert(0, str(sentinel_dir))
spec = importlib.util.spec_from_file_location("sentinelcore_ai", sentinel_dir / "main.py")
sentinel_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sentinel_mod)
sentinel_app = sentinel_mod.app


def test_incident_creation_log_forwarded(monkeypatch):
    calls: list[dict] = []

    def fake_post(url, json, timeout):
        calls.append({"url": url, "json": json})
        class Resp:
            status_code = 200
        return Resp()

    monkeypatch.setattr(requests, "post", fake_post)
    client = TestClient(incident_app)
    resp = client.post("/incident", json={"id": 1})
    assert resp.status_code == 200
    assert calls
    entry = next(call["json"] for call in calls if call["json"]["message"] == "incident_created")
    assert entry["service"] == "incident_manager"


def test_analysis_log_forwarded(monkeypatch):
    calls: list[dict] = []

    def fake_req_post(url, json, timeout):
        calls.append(json)
        class Resp:
            status_code = 200
        return Resp()

    monkeypatch.setattr(requests, "post", fake_req_post)

    class DummyResp:
        status_code = 200

    async def fake_httpx_post(self, url, json):
        return DummyResp()

    monkeypatch.setattr(httpx.AsyncClient, "post", fake_httpx_post, raising=False)

    client = TestClient(sentinel_app)
    resp = client.post("/analyze", json={"foo": "bar"})
    assert resp.status_code == 200
    assert calls
    assert calls[0]["service"] == "sentinelcore-ai"
    assert calls[0]["message"] == "analyze"
