from datetime import datetime, timedelta
import random

from config.settings import get_settings


def is_active_time(now: datetime | None = None) -> bool:
    settings = get_settings()  # FIX: убрали глобальный settings
    now = now or datetime.now()
    return settings.active_hours_start <= now.hour < settings.active_hours_end


# --- ДОБАВЛЕНО: ожидание до рабочего времени ---
def seconds_until_active(now: datetime | None = None) -> int:
    settings = get_settings()
    now = now or datetime.now()

    if is_active_time(now):
        return 0

    start_hour = settings.active_hours_start

    next_start = now.replace(hour=start_hour, minute=0, second=0, microsecond=0)

    if now.hour >= start_hour:
        next_start += timedelta(days=1)

    delta = (next_start - now).total_seconds()

    # + случайный сдвиг чтобы не стартовать в одну секунду
    jitter = random.randint(300, 1800)  # 5–30 минут

    return int(delta + jitter)