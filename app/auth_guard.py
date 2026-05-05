import logging
import portalocker
from pathlib import Path

logger = logging.getLogger(__name__)

LOCK_FILE = Path("data/RUN.lock")

_lock_file_handle = None


def acquire_lock():
    """
    Prevent parallel runs.
    Source of truth = OS lock, not file existence.
    """
    global _lock_file_handle

    LOCK_FILE.parent.mkdir(parents=True, exist_ok=True)

    _lock_file_handle = LOCK_FILE.open("a+")

    try:
        portalocker.lock(
            _lock_file_handle,
            portalocker.LockFlags.EXCLUSIVE | portalocker.LockFlags.NON_BLOCKING
        )
        logger.info("Process lock acquired")

    except portalocker.exceptions.LockException:
        _lock_file_handle.close()
        _lock_file_handle = None
        raise RuntimeError("Another instance is already running")


def release_lock():
    """
    Safe cleanup. Even if crash happened before, OS releases lock anyway.
    """
    global _lock_file_handle

    if not _lock_file_handle:
        return

    try:
        portalocker.unlock(_lock_file_handle)
    except Exception:
        pass

    try:
        _lock_file_handle.close()
    except Exception:
        pass

    _lock_file_handle = None


# --- STOP AUTH (manual kill switch only) ---

STOP_FILE = Path("data/STOP_AUTH.flag")


def check_auth_block() -> bool:
    return STOP_FILE.exists()


def create_auth_block(reason: str):
    STOP_FILE.parent.mkdir(parents=True, exist_ok=True)
    STOP_FILE.write_text(reason)


def remove_auth_block():
    try:
        STOP_FILE.unlink()
    except FileNotFoundError:
        pass