"""Application configuration settings for TaskFlow."""

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Pydantic Settings for TaskFlow backend."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    PROJECT_NAME: str = "TaskFlow API"
    VERSION: str = "0.1.0"
    ENVIRONMENT: str = "development"

    # Database connection URL
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/taskflow_db"

    # CORS configuration
    ALLOWED_ORIGINS: str | list[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: str | list[str]) -> list[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",") if i.strip()]
        elif isinstance(v, list):
            return v
        return ["http://localhost:3000"]


settings = Settings()
