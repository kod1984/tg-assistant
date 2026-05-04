from telethon import TelegramClient
from config.settings import get_settings

def create_client():
    settings = get_settings()
    
    return TelegramClient(        
        settings.session_path,
        settings.api_id,
        settings.api_hash,
        connection_retries=1,
        retry_delay=5,
        auto_reconnect=False,  # FIX: отключаем авто — управляем сами
    )
