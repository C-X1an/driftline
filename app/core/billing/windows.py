# app/core/billing/windows.py

from datetime import datetime, timedelta, timezone
from typing import Tuple


def current_month_window() -> Tuple[datetime, datetime]:
    """
    Returns UTC start and end of the current calendar month.
    """
    now = datetime.now(timezone.utc)

    start = now.replace(
        day=1,
        hour=0,
        minute=0,
        second=0,
        microsecond=0,
    )

    if start.month == 12:
        end = start.replace(year=start.year + 1, month=1)
    else:
        end = start.replace(month=start.month + 1)

    return start, end
