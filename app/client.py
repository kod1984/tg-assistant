from telethon import TelegramClient
from config.settings import settings

def create_client():
    return TelegramClient(
        settings.session_path,
        settings.api_id,
        settings.api_hash,
        connection_retries=5,
        retry_delay=5,
        auto_reconnect=True,
    )
