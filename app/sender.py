import asyncio
import random
from telethon.errors import FloodWaitError
import logging

logger = logging.getLogger(__name__)


async def human_delay():
    await asyncio.sleep(random.uniform(3, 12))


async def send_message_safe(client, target, text):
    await human_delay()

    try:
        # --- typing simulation ---
        async with client.action(target, "typing"):
            await asyncio.sleep(random.uniform(2.5, 3.5))

        await client.send_message(target, text)
        logger.info("Message sent to %s", target)

        await asyncio.sleep(random.uniform(10, 30))

    except FloodWaitError as e:
        wait_time = e.seconds + random.randint(10, 30)
        logger.warning("FloodWait: sleeping %s sec", wait_time)
        await asyncio.sleep(wait_time)