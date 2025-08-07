# Ares Core

This repository hosts the Ares Core microservices. Service endpoints and
credentials are configured through environment variables. Each variable may
also be provided via a file path using the `*_FILE` convention to support
Docker secrets or other mounted configuration files.

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
