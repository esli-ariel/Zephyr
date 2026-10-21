from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path


class Settings(BaseSettings):
    # Application
    app_name: str = "Zéphyr"
    app_env: str = "development"
    debug: bool = True
    persistence_enabled: bool = True
    database_path: str = str(
        Path(__file__).resolve().parents[1] / "data" / "zephyr.sqlite3"
    )

    # OpenRouter
    openrouter_api_key: str = ""
    openrouter_model: str = ""

    # Frontend
    frontend_url: str = "http://localhost:4000"

    # Configuration
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()
