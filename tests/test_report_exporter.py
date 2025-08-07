import os
import sys
from pathlib import Path as _Path

sys.path.insert(0, str(_Path(__file__).resolve().parents[1]))

os.environ.setdefault("LOG_INDEXER_URL", "http://log-indexer")

from report_exporter.exporter import generate_csv, sign_file, upload_to_s3
from report_exporter.app import app
from fastapi.testclient import TestClient


def test_generate_csv(tmp_path):
    logs = [{"message": "hello", "level": "INFO"}]
    out = tmp_path / "report.csv"
    generate_csv(logs, out)
    assert out.read_text().strip() == "message,level\nhello,INFO"


def test_sign_file(tmp_path):
    data = tmp_path / "data.txt"
    data.write_text("payload")
    sig_path = sign_file(data, b"secret")
    assert sig_path.exists()
    # recompute signature manually to verify
    import hmac, hashlib
    sig = sig_path.read_text()
    assert sig == hmac.new(b"secret", b"payload", hashlib.sha256).hexdigest()


def test_upload_to_s3(tmp_path):
    class DummyClient:
        def __init__(self):
            self.kwargs = None
        def put_object(self, **kwargs):
            self.kwargs = kwargs
    client = DummyClient()
    f = tmp_path / "file.csv"
    f.write_text("x")
    upload_to_s3(f, "bucket", "obj", s3_client=client)
    assert client.kwargs["Bucket"] == "bucket"
    assert client.kwargs["Key"] == "obj"
    assert "ObjectLockMode" in client.kwargs


def test_health_endpoint():
    client = TestClient(app)
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_export_endpoint(tmp_path, monkeypatch):
    from report_exporter import exporter

    monkeypatch.chdir(tmp_path)

    def fake_fetch_logs():
        return [
            {
                "timestamp": "2024-01-01T00:00:00Z",
                "level": "INFO",
                "service": "test",
                "message": "hello",
            }
        ]

    monkeypatch.setattr(exporter, "fetch_logs", fake_fetch_logs)
    client = TestClient(app)
    resp = client.get("/export")
    assert resp.status_code == 200
    assert (tmp_path / "logs_v1.csv").exists()
    assert (tmp_path / "logs_v1.pdf").exists()
