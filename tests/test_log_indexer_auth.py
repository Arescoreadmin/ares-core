import os
import importlib
import sys
from pathlib import Path as _Path
sys.path.insert(0, str(_Path(__file__).resolve().parents[1]))
from fastapi.testclient import TestClient
from log_indexer.app.dao import LogDAO


def test_log_endpoint_requires_token(tmp_path, monkeypatch):
    os.environ['LOG_INDEXER_TOKEN'] = 'secret'
    # reload module to pick up env variable
    mod = importlib.reload(importlib.import_module('log_indexer.app.main'))
    mod.dao = LogDAO(tmp_path / 'logs.db')
    client = TestClient(mod.app)
    resp = client.post('/log', json={'timestamp': '2024-01-01T00:00:00Z', 'level': 'INFO', 'service': 'test', 'message': 'hello'})
    assert resp.status_code == 401
    resp = client.post('/log', headers={'Authorization': 'Bearer secret'}, json={'timestamp': '2024-01-01T00:00:00Z', 'level': 'INFO', 'service': 'test', 'message': 'hello'})
    assert resp.status_code == 201
