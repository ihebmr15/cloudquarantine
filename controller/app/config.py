from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "CloudQuarantine"
    app_env: str = "dev"
    log_level: str = "INFO"
    response_mode: str = "monitor"
    evidence_dir: str = "../evidence/incidents"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
