# Manual Recovery Steps

With the automated self-healing supervisor removed, services need manual intervention if a container exits unexpectedly.

## Restart a service

Use the helper script:

```bash
./scripts/restart_service.sh <service-name>
```

This issues a `docker compose restart` (or `docker-compose restart`) for the given service.

## Inspect service status

List running containers to find crashed services:

```bash
docker compose ps
```

If a service is stopped, restart it using the script above or run:

```bash
docker compose up -d <service-name>
```

These steps allow operators to manually recover services until orchestration tooling is introduced.
