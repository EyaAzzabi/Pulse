from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "Pulse AI"
    environment: str = "development"

    database_url: str = "sqlite:///./pulse.db"

    jwt_secret: str = "dev-only-insecure-secret-change-me"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60 * 24 * 7

    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    # LLM provider abstraction. If no key is configured, the copilot runs in
    # deterministic offline mode (financial engine answers only, no generative text).
    llm_provider: str = "none"  # "groq" | "openai" | "none"
    llm_api_key: str | None = None
    llm_model: str = "llama-3.1-8b-instant"
    llm_base_url: str | None = None  # override for OpenAI-compatible endpoints

    n8n_webhook_url: str | None = None
    n8n_otp_webhook_url: str | None = None
    n8n_webhook_secret: str | None = None

    smtp_host: str | None = None
    smtp_port: int = 587
    smtp_user: str | None = None
    smtp_password: str | None = None
    smtp_from: str | None = None

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
