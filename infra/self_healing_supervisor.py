import os
import time
from typing import List, Tuple

import docker
import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry


def parse_targets(raw: str) -> List[Tuple[str, str]]:
    targets = []
    for item in raw.split(','):
        item = item.strip()
        if not item:
            continue
        if '=' in item:
            name, url = item.split('=', 1)
            targets.append((name.strip(), url.strip()))
    return targets


def main() -> None:
    targets_env = os.getenv('SUPERVISE_TARGETS', '')
    check_interval = int(os.getenv('CHECK_INTERVAL', '30'))
    targets = parse_targets(targets_env)
    if not targets:
        print('No targets configured for supervision', flush=True)
        return

    client = docker.DockerClient(base_url='unix://var/run/docker.sock')

    session = requests.Session()
    adapter = HTTPAdapter(max_retries=Retry(total=3, backoff_factor=0.5))
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    while True:
        for container_name, url in targets:
            try:
                response = session.get(url, timeout=5)
                healthy = response.status_code == 200
            except Exception as exc:
                print(f"Health check for {container_name} failed: {exc}")
                healthy = False

            if not healthy:
                try:
                    print(f'Restarting container {container_name}', flush=True)
                    client.containers.get(container_name).restart()
                except Exception as exc:
                    print(f'Failed to restart {container_name}: {exc}', flush=True)
        time.sleep(check_interval)


if __name__ == '__main__':
    main()
