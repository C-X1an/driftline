from sqlalchemy.orm import Session

from app.core.baselines.first_snapshot import get_baseline_snapshot


def has_valid_baseline(db: Session, source_id) -> bool:
    """
    A source has a valid baseline if it has at least one snapshot.
    """
    baseline = get_baseline_snapshot(db, source_id)
    return baseline is not None
