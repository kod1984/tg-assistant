from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    api_id: int = Field(..., description="Telegram API ID")
    api_hash: str = Field(..., min_length=10)

    session_path: str = "data/session"
    target_chat: str = "me"

    active_hours_start: int = 9
    active_hours_end: int = 23

    keywords: list[str] = Field(
        default_factory=lambda: [
            "lego",
            "printer",
            "принтер",
            "лего",
            "филамент",
            "филомент",
        ]
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )

settings = Settings()

@lru_cache
def get_settings() -> Settings:
    return Settings()