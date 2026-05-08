from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Finance Copilot API"
    environment: str = Field(default="development")
    api_prefix: str = "/api/v1"
    log_level: str = "INFO"

    database_url: str = Field(
        default="postgresql+asyncpg://postgres:postgres@db:5432/finance_copilot"
    )

    upload_dir: str = "uploads"


settings = Settings()
