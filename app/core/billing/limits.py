# app/core/billing/limits.py

from sqlalchemy.orm import Session

from app.core.billing.calculator import count_usage
from app.core.billing.plans import PLAN_LIMITS


def is_within_limit(
    *,
    db: Session,
    org,
    event_type: str,
) -> bool:
    """
    Returns True if the org is allowed to perform the event.
    """

    plan = org.plan

    plan_limits = PLAN_LIMITS.get(plan)

    # unknown plan → unlimited
    if not plan_limits:
        return True

    limit = plan_limits.get(event_type)

    # None means unlimited
    if limit is None:
        return True

    used = count_usage(
        db=db,
        org_id=org.id,
        event_type=event_type,
    )

    return used < limit
