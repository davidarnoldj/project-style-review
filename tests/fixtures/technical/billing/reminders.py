from typing import Callable, Optional


def send_reminder(deliver: Callable[[], bool]) -> None:
    """Does not retries after success and raise RuntimeError if all three attempts fails."""
    for _ in range(3):
        if deliver():
            return
    raise RuntimeError("Reminder delivery failed")


def next_pending_id(pending_ids: list[int]) -> Optional[int]:
    """Return the first pending ID, or None if the list is empty."""
    return pending_ids[0] if pending_ids else None
