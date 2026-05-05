import pytest
from datetime import datetime, timedelta

from app.runtime import ReconnectTracker


def test_reconnect_tracker_cleanup():
    tracker = ReconnectTracker()

    now = datetime.now()

    tracker.success = [
        now - timedelta(minutes=5),
        now - timedelta(minutes=15),
    ]

    tracker.cleanup(window_minutes=10)

    assert len(tracker.success) == 1


def test_reconnect_tracker_failed_limit():
    tracker = ReconnectTracker()

    for _ in range(3):
        tracker.add_failed()

    assert len(tracker.failed) == 3


def test_reconnect_tracker_success_limit():
    tracker = ReconnectTracker()

    for _ in range(2):
        tracker.add_success()

    assert len(tracker.success) == 2