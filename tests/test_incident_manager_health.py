import os
import sys
from pathlib import Path as _Path

sys.path.insert(0, str(_Path(__file__).resolve().parents[1]))

os.environ.setdefault("LOG_INDEXER_URL", "http://log-indexer")

from fastapi.testclient import TestClient
from incident_manager.app.main import app


def test_health_endpoint():
    client = TestClient(app)
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}
