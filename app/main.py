import asyncio
import logging
from pathlib import Path

from app.auth_guard import acquire_lock, release_lock
from app.runtime import ClientRunner

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


def ensure_dirs():
    Path("logs").mkdir(exist_ok=True)
    Path("data").mkdir(exist_ok=True)


async def run_app():
    runner = ClientRunner()
    await runner.run()


if __name__ == "__main__":
    try:
        acquire_lock()
        ensure_dirs()
        setup_logging()
        asyncio.run(run_app())

    finally:
        release_lock()