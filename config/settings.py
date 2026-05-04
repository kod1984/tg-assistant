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

    # --- ДОБАВЛЕНО: контроль реконнектов ---
    reconnect_window_minutes: int = 10  # окно анализа
    max_success_reconnects: int = 1     # >1 → стоп
    max_failed_reconnects: int = 2      # >=2 → стоп
    
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


@lru_cache
def get_settings() -> Settings:
    return Settings()