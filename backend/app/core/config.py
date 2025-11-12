# backend/app/core/config.py
import os
from pydantic import BaseSettings, AnyUrl, validator
from typing import Optional

class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = os.environ.get("SECRET_KEY", "a_very_secret_key_fallback")

    # Token expiry (minutes)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", 60 * 24 * 8))  # 8 days default
    REFRESH_TOKEN_EXPIRE_MINUTES: int = int(os.environ.get("REFRESH_TOKEN_EXPIRE_MINUTES", 60 * 24 * 30))  # 30 days default

    # DB: accept a plain string, but we will normalise it for asyncpg usage later
    DATABASE_URL: str = os.environ.get("DATABASE_URL", "")

    class Config:
        case_sensitive = True

    # Optionally validate / normalize DB url here (not necessary but handy)
    @validator("DATABASE_URL", pre=True)
    def normalize_database_url(cls, v: Optional[str]) -> str:
        if not v:
            return ""
        # if somebody used the short `postgres://` form, convert to SQLAlchemy asyncpg form
        if v.startswith("postgres://"):
            return v.replace("postgres://", "postgresql+asyncpg://", 1)
        # if already has asyncpg prefix, return as-is
        return v

# instantiate settings
settings = Settings()

# ---- exported module-level names for backwards-compatibility ----
ACCESS_TOKEN_EXPIRE = settings.ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRE = settings.REFRESH_TOKEN_EXPIRE_MINUTES

# convenience alias for raw DB URL (already normalized by the validator)
DATABASE_URL = settings.DATABASE_URL
