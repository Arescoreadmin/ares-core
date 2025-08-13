# Ares Core

This repository hosts the Ares Core microservices. Service endpoints and
credentials are configured through environment variables. Each variable may
also be provided via a file path using the `*_FILE` convention to support
Docker secrets or other mounted configuration files.

## Durability and Authentication

- A dedicated `log-data` volume is mounted to the `log_indexer` service so
  that audit logs survive container restarts. **Do not remove this volume**
  unless migrating to a long-term store such as OpenSearch or ELK.
- All services send logs to the indexer using bearer-token authentication.
  Provide the token via the `LOG_INDEXER_TOKEN` environment variable or a
  corresponding `LOG_INDEXER_TOKEN_FILE` secret file.
- Exported CSV and PDF reports are accompanied by a `.sha256` file containing
  the SHA-256 hash of the report to make tampering evident.

## Required environment variables

The following variables must be set for the services to start. Provide the
value directly or set a corresponding `*_FILE` variable that points at a file
containing the value.

- `LOG_INDEXER_URL` – base URL of the log indexer service.
- `INCIDENT_MANAGER_URL` – base URL of the incident manager service.

Example using Docker secrets:

```
LOG_INDEXER_URL_FILE=/run/secrets/log_indexer_url
INCIDENT_MANAGER_URL_FILE=/run/secrets/incident_manager_url
```

Optional variables such as `SIGNING_KEY` and `EXPORT_BUCKET` also support the
`*_FILE` pattern and can be supplied in the same way.

## Log Indexer Storage Plan

The `log_indexer` service currently persists audit logs to a local SQLite
database for simplicity during MVP and development. For production deployments
and demo scenarios that require richer search or dashboards, plan a migration
to a scalable backend such as OpenSearch or the ELK stack. This evolution will
provide retention and query capabilities suitable for larger volumes.
SQLite should not be used in production.

## Security Notes

The `infra/self_healing_supervisor.py` utility performs HTTP health checks on
services and is intended only for demonstration or development use. Container
restart policies are set to `on-failure`; production deployments should rely
on orchestration platforms such as Kubernetes or Docker Swarm with native
health checks for automatic restarts and recovery.
