import asyncio
import logging
from datetime import datetime, timedelta

from telethon.errors import (
    SessionPasswordNeededError,
    PhoneCodeInvalidError,
    SessionRevokedError,
)

from app.client import create_client
from app.handlers import register_handlers
from app.auth_guard import (
    check_auth_block,
    create_auth_block,
    acquire_lock,
    release_lock,
)
from app.scheduler import is_active_time, seconds_until_active
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


# --- ДОБАВЛЕНО: трекер реконнектов ---
class ReconnectTracker:
    def __init__(self):
        self.success = []
        self.failed = []

    def add_success(self):
        self.success.append(datetime.now())

    def add_failed(self):
        self.failed.append(datetime.now())

    def cleanup(self, window_minutes: int):
        cutoff = datetime.now() - timedelta(minutes=window_minutes)

        self.success = [t for t in self.success if t > cutoff]
        self.failed = [t for t in self.failed if t > cutoff]


async def run_client():
    settings = get_settings()
    tracker = ReconnectTracker()

    while True:
        if check_auth_block():
            logger.error("Auth is blocked. STOP flag present.")
            return

        if not is_active_time():
            wait = seconds_until_active()
            logger.warning(f"Outside active hours. Sleeping {wait} sec")
            await asyncio.sleep(wait)
            continue

        client = create_client()

        try:
            await client.start()
            tracker.add_success()

            register_handlers(client, settings.keywords, settings.target_chat)

            logger.info("Assistant started")

            await client.run_until_disconnected()

        except (SessionPasswordNeededError, PhoneCodeInvalidError, SessionRevokedError) as e:
            create_auth_block(str(e))
            logger.exception("Critical auth error")
            raise

        except Exception as e:
            tracker.add_failed()
            logger.exception("Reconnect failed")

        finally:
            await client.disconnect()

        # --- ЛОГИКА КОНТРОЛЯ ---
        tracker.cleanup(settings.reconnect_window_minutes)

        if len(tracker.failed) >= settings.max_failed_reconnects:
            create_auth_block("Too many failed reconnects")
            logger.error("STOP: too many failed reconnects")
            return

        if len(tracker.success) > settings.max_success_reconnects:
            create_auth_block("Too many reconnects in short time")
            logger.error("STOP: reconnect storm detected")
            return

        await asyncio.sleep(5)  # небольшой cooldown


async def main():
    if check_auth_block():
        logger.error("Auth is blocked. Remove STOP_AUTH.flag to continue.")
        return

    await run_client()


if __name__ == "__main__":
    acquire_lock()
    try:
        setup_logging()
        asyncio.run(main())
    finally:
        release_lock()