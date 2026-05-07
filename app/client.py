from telethon import TelegramClient
from config.settings import get_settings


def create_client():
    settings = get_settings()

    return TelegramClient(
        settings.session_path,
        settings.api_id,
        settings.api_hash,
        # мягкий встроенный reconnect
        auto_reconnect=True,
        connection_retries=3,
        retry_delay=5,

        timeout=30,
    )