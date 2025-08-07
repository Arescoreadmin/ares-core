from pathlib import Path
from alembic import command
from alembic.config import Config


def run_migrations() -> None:
    """Apply database migrations using Alembic."""
    config_path = Path(__file__).resolve().parents[1] / 'alembic.ini'
    if not config_path.exists():
        return
    cfg = Config(str(config_path))
    command.upgrade(cfg, 'head')
