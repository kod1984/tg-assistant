from pathlib import Path

STOP_FILE = Path("data/STOP_AUTH.flag")
LOCK_FILE = Path("data/RUN.lock")

def acquire_lock():
    if LOCK_FILE.exists():
        raise RuntimeError("Already running")
    LOCK_FILE.write_text("locked")

def release_lock():
    if LOCK_FILE.exists():
        LOCK_FILE.unlink()
        
def check_auth_block():
    return STOP_FILE.exists()

def create_auth_block(reason: str):
    STOP_FILE.parent.mkdir(parents=True, exist_ok=True)
    STOP_FILE.write_text(reason)

def remove_auth_block():
    if STOP_FILE.exists():
        STOP_FILE.unlink()
