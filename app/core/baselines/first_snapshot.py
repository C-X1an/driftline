from sqlalchemy.orm import Session
from app.core.models import Snapshot


def get_baseline_snapshot(db: Session, source_id):
    return (
        db.query(Snapshot)
        .filter(
            Snapshot.source_id == source_id,
            Snapshot.is_baseline.is_(True),
        )
        .first()
    )
