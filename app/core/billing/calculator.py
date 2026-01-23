# app/core/billing/calculator.py

from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.models.usage_event import UsageEvent
from app.core.billing.windows import current_month_window


def count_usage(
    db: Session,
    *,
    org_id,
    event_type: str,
) -> int:
    start, end = current_month_window()

    total = (
        db.query(func.coalesce(func.sum(UsageEvent.quantity), 0))
        .filter(
            UsageEvent.org_id == org_id,
            UsageEvent.event_type == event_type,
            UsageEvent.occurred_at >= start,
            UsageEvent.occurred_at < end,
        )
        .scalar()
    )

    return int(total or 0)
