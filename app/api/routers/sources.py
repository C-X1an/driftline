from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from app.api.dependencies import get_db
from app.core.models import Source, Snapshot, Incident, BaselineEvent, Explanation
from app.workers.snapshot_jobs import capture_snapshot
from app.core.explanations.baseline_key import compute_baseline_change_key



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
    # 5. Baseline explanation (idempotent)
    explanation_key = compute_baseline_change_key(
        source_id=str(source.id),
    )

    existing_explanation = (
        db.query(Explanation)
        .filter(Explanation.explanation_key == explanation_key)
        .first()
    )

    if not existing_explanation:
        prompt = f"""
A new operational baseline was set for this source.

Previous baseline:
{previous_baseline.id if previous_baseline else "None"}

New baseline:
{latest_snapshot.id}

Explain why teams reset baselines, what this implies operationally,
and what operators should verify after doing so.
"""

        content = "Baseline reset explanation pending"  # placeholder if no LLM here

        explanation = Explanation(
            explanation_key=explanation_key,
            content=content,
            model="system",
            prompt_version="baseline_v1",
        )

        db.add(explanation)

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

