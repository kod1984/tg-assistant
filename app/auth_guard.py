from pathlib import Path
import logging
import portalocker

logger = logging.getLogger(__name__)

STOP_FILE = Path("data/STOP_AUTH.flag")
LOCK_FILE = Path("data/RUN.lock")

# Дескриптор открытого файла lock
_lock_file_handle = None


def acquire_lock():
    """
    Захватывает системный lock для предотвращения параллельного запуска.
    Если предыдущий процесс упал и файл остался, пытаемся очистить.
    """
    global _lock_file_handle

    LOCK_FILE.parent.mkdir(parents=True, exist_ok=True)

    # Открываем файл (создаётся если не существует)
    _lock_file_handle = LOCK_FILE.open("a+")
    try:
        # Пытаемся получить эксклюзивный lock без блокировки
        portalocker.lock(_lock_file_handle, portalocker.LockFlags.EXCLUSIVE | portalocker.LockFlags.NON_BLOCKING)
        logger.info("Lock acquired successfully")
    except portalocker.exceptions.LockException:
        _lock_file_handle.close()
        _lock_file_handle = None
        raise RuntimeError("Another instance is already running (lock file busy)")


def release_lock():
    """Освобождает lock при завершении процесса"""
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
            # Иногда файл может быть уже удалён другим процессом
            pass


def check_auth_block():
    return STOP_FILE.exists()


def create_auth_block(reason: str):
    STOP_FILE.parent.mkdir(parents=True, exist_ok=True)
    STOP_FILE.write_text(reason)


def remove_auth_block():
    if STOP_FILE.exists():
        STOP_FILE.unlink()