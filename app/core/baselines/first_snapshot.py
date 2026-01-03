from sqlalchemy.orm import Session

from app.core.models import Snapshot, Source


def get_baseline_snapshot(db, source_id):
    source = db.query(Source).filter(Source.id == source_id).first()
    if not source or not source.monitoring_started_at:
        return None

    return (
        db.query(Snapshot)
        .filter(
            Snapshot.source_id == source_id,
            Snapshot.is_baseline.is_(True),
        )
        .first()
    )


