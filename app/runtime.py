import asyncio
import logging
from telethon.errors import SessionRevokedError

from app.client import create_client
from app.handlers import register_handlers
from app.auth_guard import check_auth_block, create_auth_block
from config.settings import get_settings


logger = logging.getLogger(__name__)


class ClientRunner:
    def __init__(self):
        self.settings = get_settings()
        self.client = create_client()
        self._running = False

    async def run(self):
        if check_auth_block():
            logger.error("Auth blocked (STOP_AUTH flag exists)")
            return

        register_handlers(
            self.client,
            self.settings.keywords,
            self.settings.target_chat,
        )

        await self._safe_start()

        logger.info("Assistant started")

        self._running = True

        while self._running:
            try:
                await self.client.run_until_disconnected()

            except SessionRevokedError as e:
                logger.critical("SESSION REVOKED by Telegram: %s", e)

                create_auth_block("Session revoked by Telegram")

                await self._safe_shutdown()

                # важно: выходим полностью, чтобы не плодить новые сессии
                raise SystemExit

            except Exception as e:
                logger.exception("Runtime crash: %s", e)

                await asyncio.sleep(5)

    async def _safe_start(self):
        try:
            await self.client.start()
        except Exception as e:
            logger.exception("Failed to start client: %s", e)
            raise

    async def _safe_shutdown(self):
        try:
            await self.client.disconnect()
        except Exception:
            pass