"""
Intervia Backend — Application Configuration
Uses pydantic-settings to load from environment variables / .env file.
"""

from functools import lru_cache
from typing import List

from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ---- Application --------------------------------------
    APP_ENV: str = "development"
    APP_VERSION: str = "0.1.0"
    APP_NAME: str = "Intervia API"
    DEBUG: bool = True

    # ---- Server -------------------------------------------
    BACKEND_HOST: str = "0.0.0.0"
    BACKEND_PORT: int = 8000
    BACKEND_RELOAD: bool = True

    # ---- CORS ---------------------------------------------
    ALLOWED_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    @property
    def cors_origins(self) -> List[str]:
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",") if o.strip()]

    # ---- Database -----------------------------------------
    DATABASE_URL: str = "postgresql+asyncpg://postgres:password@localhost:5432/intervia"

    # ---- Supabase -----------------------------------------
    SUPABASE_URL: str = ""
    SUPABASE_ANON_KEY: str = ""
    SUPABASE_SERVICE_ROLE_KEY: str = ""

    # ---- AI / LLM -----------------------------------------
    GEMINI_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    LLM_PROVIDER: str = "gemini"
    LLM_MODEL: str = "gemini-2.0-flash-exp"

    # ---- Embeddings ---------------------------------------
    EMBEDDING_MODEL: str = "models/text-embedding-004"
    EMBEDDING_DIMENSION: int = 768

    # ---- Voice --------------------------------------------
    STT_PROVIDER: str = "google"
    GOOGLE_STT_API_KEY: str = ""
    TTS_PROVIDER: str = "google"
    GOOGLE_TTS_API_KEY: str = ""
    ELEVENLABS_API_KEY: str = ""

    # ---- Auth / JWT ---------------------------------------
    JWT_SECRET_KEY: str = "changeme-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ---- File Storage -------------------------------------
    STORAGE_PROVIDER: str = "local"
    LOCAL_STORAGE_PATH: str = "./uploads"
    MAX_UPLOAD_SIZE_MB: int = 10


@lru_cache
def get_settings() -> Settings:
    """Cached settings singleton. Import and call this everywhere."""
    return Settings()
