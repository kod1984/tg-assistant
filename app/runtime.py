# app/runtime.py

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
from app.auth_guard import check_auth_block, create_auth_block
from app.scheduler import is_active_time, seconds_until_active
from config.settings import get_settings


logger = logging.getLogger(__name__)


class ReconnectTracker:
    def __init__(self):
        self.success: list[datetime] = []
        self.failed: list[datetime] = []

    def add_success(self):
        self.success.append(datetime.now())

    def add_failed(self):
        self.failed.append(datetime.now())

    def cleanup(self, window_minutes: int):
        cutoff = datetime.now() - timedelta(minutes=window_minutes)

        self.success = [t for t in self.success if t > cutoff]
        self.failed = [t for t in self.failed if t > cutoff]


class ClientRunner:
    def __init__(self):
        self.settings = get_settings()
        self.tracker = ReconnectTracker()

    async def run(self):
        while True:
            if check_auth_block():
                logger.error("Auth is blocked. STOP flag present.")
                return

            if not is_active_time():
                wait = seconds_until_active()
                logger.warning(f"Outside active hours. Sleeping {wait} sec")
                await asyncio.sleep(wait)
                continue

            await self._run_once()

            self._post_run_checks()

            await asyncio.sleep(5)

    async def _run_once(self):
        client = create_client()

        try:
            await client.start()
            self.tracker.add_success()

            register_handlers(
                client,
                self.settings.keywords,
                self.settings.target_chat,
            )

            logger.info("Assistant started")

            await client.run_until_disconnected()

        except (SessionPasswordNeededError, PhoneCodeInvalidError, SessionRevokedError) as e:
            create_auth_block(str(e))
            logger.exception("Critical auth error")
            raise

        except Exception:
            self.tracker.add_failed()
            logger.exception("Reconnect failed")

        finally:
            await client.disconnect()

    def _post_run_checks(self):
        s = self.settings

        self.tracker.cleanup(s.reconnect_window_minutes)

        if len(self.tracker.failed) >= s.max_failed_reconnects:
            create_auth_block("Too many failed reconnects")
            logger.error("STOP: too many failed reconnects")
            raise SystemExit

        if len(self.tracker.success) > s.max_success_reconnects:
            create_auth_block("Too many reconnects in short time")
            logger.error("STOP: reconnect storm detected")
            raise SystemExit