"""Application configuration and environment settings."""

import os
from functools import lru_cache
from pathlib import Path


def _load_env_file(dotenv_path: Path) -> None:
    """Load key-value pairs from a .env file into os.environ if not already set."""
    if not dotenv_path.is_file():
        return
    with open(dotenv_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, val = line.split("=", 1)
            key = key.strip()
            val = val.strip().strip("'\"")
            if key not in os.environ:
                os.environ[key] = val


# Attempt to load local .env if present
_env_path = Path(__file__).resolve().parent.parent.parent / ".env"
_load_env_file(_env_path)


class Settings:
    """Application settings resolved from environment variables."""

    def __init__(self) -> None:
        self.app_name: str = os.getenv("APP_NAME", "Persistent Data Layer")
        self.app_env: str = os.getenv("APP_ENV", "development")
        self.app_version: str = os.getenv("APP_VERSION", "1.0.0")
        self.debug: bool = os.getenv("DEBUG", "true").lower() in ("true", "1", "yes")
        self.api_prefix: str = os.getenv("API_PREFIX", "/api/v1")
        self.host: str = os.getenv("HOST", "0.0.0.0")
        self.port: int = int(os.getenv("PORT", "8000"))

        # Database connection string
        # Normalizes postgresql:// to postgresql+psycopg:// for modern psycopg3 driver support
        raw_db_url = os.getenv("DATABASE_URL", "sqlite:///./persistent_data.db")
        if raw_db_url.startswith("postgresql://"):
            raw_db_url = raw_db_url.replace("postgresql://", "postgresql+psycopg://", 1)
        self.database_url: str = raw_db_url

        # Database pool settings
        self.db_pool_size: int = int(os.getenv("DB_POOL_SIZE", "10"))
        self.db_max_overflow: int = int(os.getenv("DB_MAX_OVERFLOW", "20"))
        self.db_pool_timeout: int = int(os.getenv("DB_POOL_TIMEOUT", "30"))
        self.db_pool_pre_ping: bool = os.getenv("DB_POOL_PRE_PING", "true").lower() in ("true", "1", "yes")

        # CORS origins parsing
        raw_origins = os.getenv(
            "CORS_ORIGINS",
            "http://localhost:3000,http://localhost:5173,http://127.0.0.1:3000,http://127.0.0.1:5173",
        )
        self.cors_origins: list[str] = [
            origin.strip() for origin in raw_origins.split(",") if origin.strip()
        ]

        # Seed data configuration
        self.seed_data_on_startup: bool = os.getenv(
            "SEED_DATA_ON_STARTUP", "true"
        ).lower() in ("true", "1", "yes")


@lru_cache()
def get_settings() -> Settings:
    """Provide a cached singleton instance of Settings."""
    return Settings()
