from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.core.models import Incident

router = APIRouter(prefix="/incidents", tags=["incidents"])


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
