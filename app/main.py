import asyncio
import logging
from pathlib import Path

from telethon.errors import (
    SessionPasswordNeededError,
    PhoneCodeInvalidError,
    SessionRevokedError,
)

from app.client import create_client
from app.handlers import register_handlers
from app.auth_guard import check_auth_block, create_auth_block, acquire_lock, release_lock
from config.settings import get_settings


logger = logging.getLogger(__name__)


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        handlers=[
            logging.FileHandler("logs/app.log"),
            logging.StreamHandler(),
        ],
    )


async def main():
    settings = get_settings()

    if check_auth_block():
        logger.error("Auth is blocked. Remove STOP_AUTH.flag to continue.")
        return

    client = create_client()

    try:
        await client.start()
    except (SessionPasswordNeededError, PhoneCodeInvalidError, SessionRevokedError) as e:
        create_auth_block(str(e))
        logger.exception("Authentication failed")
        raise

    register_handlers(client, settings.keywords, settings.target_chat)

    logger.info("Assistant started")

    try:
        await client.run_until_disconnected()
    except SessionRevokedError as e:
        create_auth_block(f"Session revoked: {e}")
        logger.exception("Session revoked — blocking restart")
        raise  # важно чтобы процесс умер        
        
    finally:
        logger.info("Shutting down client")
        await client.disconnect()

def ensure_dirs():
    Path("logs").mkdir(exist_ok=True)
    Path("data").mkdir(exist_ok=True)

if __name__ == "__main__":
    acquire_lock()
    try:
        ensure_dirs()
        setup_logging()
        asyncio.run(main())
    finally:
        release_lock()        