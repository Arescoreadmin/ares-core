#!/usr/bin/env bash
# Simple script to manually restart a service container.
# Usage: ./scripts/restart_service.sh <service-name>
set -euo pipefail
if [ $# -ne 1 ]; then
  echo "Usage: $0 <service-name>" >&2
  exit 1
fi
SERVICE=$1
if command -v docker-compose >/dev/null 2>&1; then
  docker-compose restart "$SERVICE"
else
  docker compose restart "$SERVICE"
fi
