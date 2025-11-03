from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    mongo_uri: str = Field(default="mongodb://localhost:27017", alias="MONGO_URI")
    mongo_db: str = Field(default="chatbot_ai", alias="MONGO_DB")

    ai_provider: str = Field(default="ollama", alias="AI_PROVIDER")
    openai_api_key: str | None = Field(default=None, alias="OPENAI_API_KEY")
    ollama_base_url: str = Field(default="http://localhost:11434", alias="OLLAMA_BASE_URL")

    telegram_bot_token: str | None = Field(default=None, alias="TELEGRAM_BOT_TOKEN")
    green_api_instance_id: str | None = Field(default=None, alias="GREEN_API_INSTANCE_ID")
    green_api_token: str | None = Field(default=None, alias="GREEN_API_TOKEN")

    admin_api_key: str = Field(default="changeme", alias="ADMIN_API_KEY")
    session_cookie_name: str = Field(default="admin_session")
    session_max_age_seconds: int = Field(default=60 * 60 * 12)

    log_level: str = Field(default="INFO", alias="LOG_LEVEL")


@lru_cache
def get_settings() -> Settings:
    """Return a cached application settings instance."""

    return Settings()


settings = get_settings()
