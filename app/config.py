import os
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings


def choose_env_file() -> Path:
    """Depending on environment variable `ENV` value return name of dotenv file in the
    `app` directory. Cut numbers from filename if any. If no `ENV` or empty value
    consider "local".
    For example:
        - "dev" -> ".env.dev"
        - "prod" -> ".env.prod"
        - "" -> ".env.local"
    """
    current_env = os.getenv("ENV") or "local"
    current_dir = Path(__file__).parent
    return current_dir / f".env.{''.join([x for x in current_env if not x.isdigit()])}"


class Settings(BaseSettings):
    LOGGING_LEVEL: str = "DEBUG"
    DATABASE_URL: str = "sqlite+aiosqlite:///./stocks.db"
    STOCK_INDEX_NAME: str = "mcap_100"

    class Config:
        env_file = choose_env_file()


@lru_cache()
def get_settings():
    return Settings()
