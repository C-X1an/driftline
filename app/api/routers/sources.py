from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from app.api.dependencies import get_db
from app.core.models import Source, Snapshot, Incident, BaselineEvent
from app.workers.snapshot_jobs import capture_snapshot



router = APIRouter(prefix="/sources", tags=["sources"])


@router.get("/")
def list_sources(db: Session = Depends(get_db)):
    sources = db.query(Source).all()

    return [
        {
            "id": str(source.id),
            "name": source.name,
            "type": source.type,
            "active": source.active,
        }
        for source in sources
    ]

@router.post("/{source_id}/reset-baseline")
def reset_baseline(
    source_id: str,
    db: Session = Depends(get_db),
):
    source = db.query(Source).filter(Source.id == source_id).first()
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")

    # 1. Capture a fresh snapshot
    capture_snapshot(db, source)

    latest_snapshot = (
        db.query(Snapshot)
        .filter(Snapshot.source_id == source.id)
        .order_by(Snapshot.captured_at.desc())
        .first()
    )

    previous_baseline = (
        db.query(Snapshot)
        .filter(
            Snapshot.source_id == source.id,
            Snapshot.is_baseline.is_(True),
        )
        .first()
    )

    if not latest_snapshot:
        raise HTTPException(
            status_code=500,
            detail="Failed to capture baseline snapshot",
        )

    # 2. Clear previous baselines
    db.query(Snapshot).filter(
        Snapshot.source_id == source.id,
        Snapshot.is_baseline.is_(True),
    ).update({Snapshot.is_baseline: False})

    # 3. Set new baseline
    latest_snapshot.is_baseline = True

    # 4. Resolve all active incidents
    now = datetime.now(timezone.utc)
    active_incidents = (
        db.query(Incident)
        .filter(
            Incident.source_id == source.id,
            Incident.status.in_(["OPEN", "ACKED"]),
        )
        .all()
    )

    for incident in active_incidents:
        incident.status = "RESOLVED"
        incident.resolved_at = now

    db.add(
    BaselineEvent(
        source_id=source.id,
        snapshot_id=latest_snapshot.id,
        triggered_by="API",
    )
)
    db.commit()

    return {
        "source_id": source.id,
        "baseline_snapshot_id": latest_snapshot.id,
        "previous_baseline_snapshot_id": (
            previous_baseline.id if previous_baseline else None
        ),
        "resolved_incidents": len(active_incidents),
        "message": "Baseline reset successfully",
    }

