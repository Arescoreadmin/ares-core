import importlib
import os

import httpx
from fastapi.testclient import TestClient


class DummyResponse:
    def __init__(self):
        self.status_code = 200
    def raise_for_status(self):
        pass


def setup_module(module):
    os.environ.setdefault("ORCHESTRATOR_URL", "http://orchestrator/alert")
    os.environ.setdefault("LOG_INDEXER_URL", "http://indexer/log")
    os.environ.setdefault("LOG_INDEXER_TOKEN", "token")


def test_anomaly_triggers_alert(monkeypatch):
    calls = []

    def fake_post(url, json=None, headers=None, timeout=None):
        calls.append((url, json, headers))
        return DummyResponse()

    monkeypatch.setattr(httpx, "post", fake_post)

    mod = importlib.reload(importlib.import_module("behavior_analytics.app.main"))
    client = TestClient(mod.app)

    event = {
        "timestamp": "2024-01-01T00:00:00Z",
        "level": "ERROR",
        "service": "auth",
        "message": "failed login"
    }
    resp = client.post("/event", json=event)
    assert resp.status_code == 200
    assert resp.json()["anomalous"] is True
    alert_calls = [c for c in calls if c[0] == os.environ["ORCHESTRATOR_URL"]]
    assert alert_calls, "alert not sent"
    alert_payload = alert_calls[0][1]
    assert "risk_score" in alert_payload and "summary" in alert_payload


def test_health_survives_alert_failure(monkeypatch):
    def failing_post(url, json=None, headers=None, timeout=None):
        raise httpx.HTTPError("boom")

    monkeypatch.setattr(httpx, "post", failing_post)

    mod = importlib.reload(importlib.import_module("behavior_analytics.app.main"))
    client = TestClient(mod.app)

    event = {
        "timestamp": "2024-01-01T00:00:00Z",
        "level": "ERROR",
        "service": "auth",
        "message": "failed login"
    }
    # Should not raise even if posting fails
    resp = client.post("/event", json=event)
    assert resp.status_code == 200
    health = client.get("/health")
    assert health.status_code == 200
    assert health.json()["status"] == "ok"
