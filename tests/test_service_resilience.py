import sys
import time
import multiprocessing
from pathlib import Path as _Path

sys.path.insert(0, str(_Path(__file__).resolve().parents[1]))

from fastapi.testclient import TestClient
from report_exporter.app import app as exporter_app
from incident_manager.app.main import app as incident_app


def _run_exporter():
    client = TestClient(exporter_app)
    while True:
        client.get("/health")
        time.sleep(0.2)


def test_services_survive_module_exit():
    proc = multiprocessing.Process(target=_run_exporter)
    proc.start()
    time.sleep(0.5)
    proc.terminate()
    proc.join()

    incident_client = TestClient(incident_app)
    resp = incident_client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}
