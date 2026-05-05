from telethon import TelegramClient
from config.settings import get_settings


def create_client():
    settings = get_settings()

    return TelegramClient(
        settings.session_path,
        settings.api_id,
        settings.api_hash,
        connection_retries=5,
        retry_delay=3,
        auto_reconnect=True,   # ВАЖНО: пусть держит соединение сам
        timeout=30,
    )