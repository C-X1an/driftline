from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.core.models import Incident, DriftSignal, Explanation

router = APIRouter(prefix="/incidents", tags=["incidents"])


@router.get("/{incident_id}")
def get_incident_timeline(
    incident_id: str,
    db: Session = Depends(get_db),
):
    incident = (
        db.query(Incident)
        .filter(Incident.id == incident_id)
        .first()
    )

    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")   

    drift_signal = (
        db.query(DriftSignal)
        .filter(
            DriftSignal.source_id == incident.source_id,
            DriftSignal.drift_fingerprint == incident.drift_fingerprint,
        )
        .order_by(DriftSignal.computed_at.desc())
        .first()
    )

    explanation = (
        db.query(Explanation)
        .filter(Explanation.id == incident.explanation_id)
        .first()
        if incident.explanation_id
        else None
    )

    timeline = []

    timeline.append({
        "type": "INCIDENT_CREATED",
        "at": incident.first_seen_at,
    })

    if explanation:
        timeline.append({
            "type": "EXPLANATION_ATTACHED",
            "at": explanation.created_at,
        })

    if incident.status == "ACKED":
        timeline.append({
            "type": "INCIDENT_ACKED",
            "at": incident.last_seen_at,
        })

    if incident.resolved_at:
        timeline.append({
            "type": "INCIDENT_RESOLVED",
            "at": incident.resolved_at,
        })

    return {
        "incident": {
            "id": str(incident.id),
            "status": incident.status,
            "risk_level": incident.current_risk_level,
            "magnitude": incident.current_magnitude,
            "origin": incident.origin,
            "first_seen_at": incident.first_seen_at,
            "last_seen_at": incident.last_seen_at,
            "resolved_at": incident.resolved_at,
        },
        "drift": {
            "fingerprint": incident.drift_fingerprint,
            "baseline_snapshot_id": (
                str(drift_signal.baseline_snapshot_id)
                if drift_signal else None
            ),
            "current_snapshot_id": (
                str(drift_signal.current_snapshot_id)
                if drift_signal else None
            ),
            "components": (
                drift_signal.components if drift_signal else []
            ),
        },
        "explanation": {
            "id": str(explanation.id),
            "content": explanation.content,
            "model": explanation.model,
            "created_at": explanation.created_at,
        } if explanation else None,
        "timeline": timeline,
    }
