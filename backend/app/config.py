import os


def get_database_url() -> str:
    """Retrieve the database URL from environment variables or secret files.

    This function checks the ``DATABASE_URL`` environment variable first. If it
    is not set, it will look for ``DATABASE_URL_FILE`` which should point to a
    file containing the URL (useful for Docker secrets or other secret
    managers). If neither is provided, a ``RuntimeError`` is raised.
    """
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        secret_file = os.getenv("DATABASE_URL_FILE")
        if secret_file and os.path.exists(secret_file):
            with open(secret_file, "r", encoding="utf-8") as fh:
                db_url = fh.read().strip()
    if not db_url:
        raise RuntimeError("DATABASE_URL is not configured")
    return db_url
