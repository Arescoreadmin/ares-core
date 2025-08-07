# Behavior Analytics Service

FastAPI microservice analyzing log events for suspicious behavior.

## Endpoints

- `GET /health` – health check.
- `POST /event` – analyze a log event. Expects JSON:
  ```json
  {
    "timestamp": "2024-01-01T00:00:00Z",
    "level": "INFO",
    "service": "example",
    "message": "user login failed"
  }
  ```
  Returns `{ "anomalous": true|false }`.

## Environment Variables

- `ORCHESTRATOR_URL` – URL to send alerts to SentinelCore orchestrator.
- `LOG_INDEXER_URL` – URL of the log indexer `/log` endpoint.
- `LOG_INDEXER_TOKEN` – Bearer token for log indexer authentication.
