from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Application
    app_name: str = "Zéphyr"
    app_env: str = "development"
    debug: bool = True

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