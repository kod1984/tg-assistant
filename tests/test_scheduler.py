from datetime import datetime
from app.scheduler import is_active_time


def test_active_time_inside_range():
    dt = datetime(2024, 1, 1, 10, 0)

    assert is_active_time(dt) is True


def test_active_time_outside_range():
    dt = datetime(2024, 1, 1, 3, 0)

    assert is_active_time(dt) is False