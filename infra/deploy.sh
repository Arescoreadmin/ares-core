#!/usr/bin/env bash
set -e

# Navigate to project backend directory
cd "$(dirname "$0")/../backend"

# Apply database migrations
alembic upgrade head

# Execute the command passed to the script (e.g., start server)
exec "$@"
