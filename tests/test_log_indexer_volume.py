import yaml
from pathlib import Path

def test_log_indexer_has_persistent_volume():
    compose = yaml.safe_load(Path('infra/docker-compose.yml').read_text())
    services = compose.get('services', {})
    log_indexer = services.get('log_indexer', {})
    assert 'volumes' in log_indexer, 'log_indexer service must define volumes'
    assert 'log-data:/var/lib/log_indexer' in log_indexer['volumes'], 'log_indexer must mount log-data volume'
    volumes = compose.get('volumes', {})
    assert 'log-data' in volumes, 'log-data volume must be declared'
