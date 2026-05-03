from datetime import datetime
from config.settings import settings

def is_active_time(now: datetime | None = None) -> bool:
    now = now or datetime.now()
    return settings.active_hours_start <= now.hour < settings.active_hours_end