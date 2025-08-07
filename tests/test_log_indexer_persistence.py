import os
import importlib
import sys
from pathlib import Path as _Path
sys.path.insert(0, str(_Path(__file__).resolve().parents[1]))
from fastapi.testclient import TestClient


def test_log_data_persists_across_restart(tmp_path, monkeypatch):
    monkeypatch.setenv('LOG_INDEXER_DATA_DIR', str(tmp_path))
    monkeypatch.setenv('LOG_INDEXER_TOKEN', 'secret')
    mod = importlib.reload(importlib.import_module('log_indexer.app.main'))
    client = TestClient(mod.app)
    payload = {
        'timestamp': '2024-01-01T00:00:00Z',
        'level': 'INFO',
        'service': 'test',
        'message': 'hello',
    }
    resp = client.post('/log', headers={'Authorization': 'Bearer secret'}, json=payload)
    assert resp.status_code == 201
    mod.dao._conn.close()
    mod = importlib.reload(mod)
    client = TestClient(mod.app)
    resp = client.get('/query')
    assert resp.status_code == 200
    assert resp.json()[0]['message'] == 'hello'
