from pathlib import Path
import logging
import portalocker
import sys

logger = logging.getLogger(__name__)

STOP_FILE = Path("data/STOP_AUTH.flag")
LOCK_FILE = Path("data/RUN.lock")

_lock_file_handle = None


def acquire_lock():
    global _lock_file_handle

    LOCK_FILE.parent.mkdir(parents=True, exist_ok=True)

    _lock_file_handle = LOCK_FILE.open("a+")
    portalocker.lock(
        _lock_file_handle,
        portalocker.LockFlags.EXCLUSIVE | portalocker.LockFlags.NON_BLOCKING
    )

    logger.info("Lock acquired successfully")


def guarded_acquire_lock():
    """
    Обёртка с try/except — используется в main
    """
    try:
        acquire_lock()
    except portalocker.exceptions.LockException:
        logger.error("Another instance is already running (lock file busy)")
        sys.exit(1)


def release_lock():
    global _lock_file_handle

    if _lock_file_handle:
        try:
            portalocker.unlock(_lock_file_handle)
        except Exception as e:
            logger.warning("Failed to unlock file: %s", e)
        finally:
            _lock_file_handle.close()
            _lock_file_handle = None

    if LOCK_FILE.exists():
        try:
            LOCK_FILE.unlink()
        except Exception:
            pass


def check_auth_block():
    return STOP_FILE.exists()


def create_auth_block(reason: str):
    STOP_FILE.parent.mkdir(parents=True, exist_ok=True)
    STOP_FILE.write_text(reason)


def remove_auth_block():
    if STOP_FILE.exists():
        STOP_FILE.unlink()