from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.core.models import Incident

router = APIRouter(prefix="/incidents", tags=["incidents"])

@router.get("")
def list_incidents(
    status: str | None = None,
    db: Session = Depends(get_db),
):
    query = db.query(Incident)

    if status:
        query = query.filter(Incident.status == status)

    incidents = (
        query
        .order_by(Incident.first_seen_at.desc())
        .limit(50)
        .all()
    )

    return [
        {
            "id": str(i.id),
            "status": i.status,
            "risk_level": i.current_risk_level,
            "magnitude": i.current_magnitude,
            "origin": i.origin,
            "first_seen_at": i.first_seen_at,
            "last_seen_at": i.last_seen_at,
            "resolved_at": i.resolved_at,
            "explanation_id": str(i.explanation_id) if i.explanation_id else None,
        }
        for i in incidents
    ]


@router.patch("/{incident_id}/ack")
def acknowledge_incident(
    incident_id: str,
    db: Session = Depends(get_db),
):
    incident = db.query(Incident).filter(Incident.id == incident_id).first()

    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    if incident.status == "RESOLVED":
        raise HTTPException(
            status_code=400,
            detail="Cannot acknowledge a resolved incident",
        )

    incident.status = "ACKED"
    db.commit()

    return {
        "incident_id": incident.id,
        "status": incident.status,
    }


