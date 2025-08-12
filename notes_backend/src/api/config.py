import os
from functools import lru_cache
from typing import List, Optional

from dotenv import load_dotenv

# Load environment variables from .env (if present), without failing when absent.
load_dotenv()


class Settings:
    """Application settings loaded from environment variables."""

    def __init__(
        self,
        app_title: Optional[str] = None,
        app_description: Optional[str] = None,
        app_version: Optional[str] = None,
        cors_allow_origins: Optional[str] = None,
        notes_db_path: Optional[str] = None,
    ) -> None:
        # App metadata
        self.app_title: str = app_title or os.getenv("APP_TITLE", "Notes API")
        self.app_description: str = app_description or os.getenv(
            "APP_DESCRIPTION",
            "A simple FastAPI backend for managing notes (create, list, fetch, update, delete).",
        )
        self.app_version: str = app_version or os.getenv("APP_VERSION", "0.1.0")

        # CORS configuration (comma-separated origins). Use "*" to allow all.
        self.cors_allow_origins_raw: str = cors_allow_origins or os.getenv("CORS_ALLOW_ORIGINS", "*")

        # Database configuration: SQLite file path. Use ':memory:' for ephemeral DB.
        # Default to a file 'notes.db' in the current working directory.
        self.notes_db_path: str = notes_db_path or os.getenv("NOTES_DB_PATH", "notes.db")

    # PUBLIC_INTERFACE
    def cors_allow_origins(self) -> List[str]:
        """Return the CORS origins as a list, handling '*' as a wildcard."""
        raw = (self.cors_allow_origins_raw or "").strip()
        if raw == "" or raw == "*":
            return ["*"]
        # Split by comma, trim whitespace, drop empty values
        return [o.strip() for o in raw.split(",") if o.strip()]

    def __repr__(self) -> str:  # For debugging purposes
        return (
            f"Settings(app_title={self.app_title!r}, app_version={self.app_version!r}, "
            f"notes_db_path={self.notes_db_path!r}, cors_allow_origins_raw={self.cors_allow_origins_raw!r})"
        )


# PUBLIC_INTERFACE
@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Get cached Settings instance loaded from environment variables."""
    return Settings()
