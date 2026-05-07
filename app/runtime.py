# app/runtime.py

import asyncio
import logging
import random

from telethon.errors import SessionRevokedError

from app.client import create_client
from app.handlers import register_handlers
from app.auth_guard import (
    check_auth_block,
    create_auth_block,
)
from app.scheduler import (
    is_active_time,
    seconds_until_active,
)
from config.settings import get_settings

logger = logging.getLogger(__name__)


class ClientRunner:
    def __init__(self):

        self.settings = get_settings()

        # ORIGINAL DESIGN RESTORED
        self.client = create_client()

        register_handlers(
            self.client,
            self.settings.keywords,
            self.settings.target_chat,
        )

        self._running = False

        self._shutdown_scheduled = False
        self._shutdown_delay_seconds = 0

    async def run(self):

        if check_auth_block():

            logger.error(
                "Auth blocked (STOP_AUTH flag exists)"
            )

            return

        self._running = True

        while self._running:

            # =====================================
            # OFF HOURS
            # =====================================

            if not is_active_time():

                sleep_time = seconds_until_active()

                logger.info(
                    "Outside active hours. "
                    "Client disconnected. "
                    "Sleeping %s seconds until next start",
                    sleep_time,
                )

                await self._safe_shutdown()

                self._shutdown_scheduled = False
                self._shutdown_delay_seconds = 0

                await asyncio.sleep(sleep_time)

                continue

            # =====================================
            # ACTIVE HOURS
            # =====================================

            try:

                await self._safe_start()

                logger.info("Assistant started")

                self._shutdown_scheduled = False
                self._shutdown_delay_seconds = 0

                # =================================
                # ACTIVE LOOP
                # =================================

                while True:

                    # connection lost
                    if not self.client.is_connected():

                        logger.warning(
                            "Client disconnected unexpectedly"
                        )

                        break

                    # working hours ended
                    if not is_active_time():

                        if not self._shutdown_scheduled:

                            self._shutdown_delay_seconds = random.randint(
                                180,   # 3 min
                                1500,  # 25 min
                            )

                            self._shutdown_scheduled = True

                            logger.info(
                                "Active window ended. "
                                "Shutdown scheduled in %s seconds",
                                self._shutdown_delay_seconds,
                            )

                        logger.info(
                            "Waiting shutdown jitter before disconnect"
                        )

                        await asyncio.sleep(
                            self._shutdown_delay_seconds
                        )

                        logger.info(
                            "Disconnecting due to inactive hours"
                        )

                        await self._safe_shutdown()

                        break

                    await asyncio.sleep(60)

            except SessionRevokedError as e:

                logger.critical(
                    "SESSION REVOKED by Telegram: %s",
                    e,
                )

                create_auth_block(
                    "Session revoked by Telegram"
                )

                await self._safe_shutdown()

                raise SystemExit

            except Exception as e:

                logger.exception(
                    "Runtime crash: %s",
                    e,
                )

                await self._safe_shutdown()

                await asyncio.sleep(15)

    async def _safe_start(self):

        # уже подключен
        if self.client.is_connected():
            return

        try:

            logger.info(
                "Connecting Telegram client"
            )

            await self.client.start()

            logger.info(
                "Telegram client connected"
            )

        except Exception as e:

            logger.exception(
                "Failed to start client: %s",
                e,
            )

            raise

    async def _safe_shutdown(self):

        try:

            if self.client.is_connected():

                logger.info(
                    "Disconnecting Telegram client"
                )

                await self.client.disconnect()

                logger.info(
                    "Telegram client disconnected"
                )

        except Exception as e:

            logger.warning(
                "Disconnect failed: %s",
                e,
            )