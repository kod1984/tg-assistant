from telethon import events
import logging

from app.filters import match_keywords
from app.sender import send_message_safe
from app.scheduler import is_active_time

logger = logging.getLogger(__name__)


def should_process(event) -> bool:
    if not event.message:
        return False

    if not event.message.text:
        return False

    if not is_active_time():
        return False

    return True


def format_message(found: list[str], text: str) -> str:
    return f"🔍 Найдено: {', '.join(found)}\n\n💬 {text}"


async def process_message(client, event, keywords, target):
    text = event.message.text
    found = match_keywords(text, keywords)

    if not found:
        logger.info("Message skipped (no keywords): %s", text)
        return

    logger.info("Keywords found %s in message: %s", found, text)

    message = format_message(found, text)
    await send_message_safe(client, target, message)


def register_handlers(client, keywords, target):

    @client.on(events.NewMessage)
    async def handler(event):
        if not should_process(event):
            return

        await process_message(client, event, keywords, target)