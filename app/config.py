from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str = "postgresql+psycopg2://aios:aios@postgres:5432/aios"
    redis_url: str = "redis://redis:6379/0"

    sentry_dsn: str | None = None

    anthropic_api_key: str | None = None
    huggingface_api_key: str | None = None
    llm_model: str = "meta-llama/Llama-2-7b-chat-hf"

    whatsapp_verify_token: str | None = None
    whatsapp_app_secret: str | None = None
    whatsapp_phone_number_id: str | None = None
    whatsapp_access_token: str | None = None

    slack_bot_token: str | None = None
    slack_signing_secret: str | None = None
    slack_deploy_webhook: str | None = None

    telegram_bot_token: str | None = None
    telegram_webhook_secret: str | None = None

    context_hub_path: str = "/app/context-hub"
    context_hub_repo: str | None = None


settings = Settings()

