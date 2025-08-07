"""Generate logging_config.py for each service from a shared template."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = (ROOT / "scripts" / "logging_config_template.py").read_text()

SERVICES = {
    "backend": ROOT / "backend" / "app" / "logging_config.py",
    "incident_manager": ROOT / "incident_manager" / "logging_config.py",
    "report_exporter": ROOT / "report_exporter" / "logging_config.py",
    "sentinelcore-ai": ROOT / "sentinelcore-ai" / "logging_config.py",
}

for name, path in SERVICES.items():
    content = TEMPLATE.replace("__SERVICE_NAME__", name)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)
    print(f"wrote {path}")
