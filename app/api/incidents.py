from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.core.models import Incident, Explanation, RiskAssessment
from app.core.explanations.policy import should_generate_explanation
from app.workers.explanation_jobs import generate_explanation
from app.llm.client import get_llm_client  # adjust if your path differs

router = APIRouter(prefix="/incidents", tags=["incidents"])


@router.get("/")
def list_incidents(db: Session = Depends(get_db)):
    incidents = (
        db.query(Incident)
        .order_by(Incident.last_seen_at.desc())
        .all()
    )

    return [
        {
            "id": str(i.id),
            "source_id": str(i.source_id),
            "status": i.status,
            "risk_level": i.current_risk_level,
            "magnitude": i.current_magnitude,
            "first_seen_at": i.first_seen_at,
            "last_seen_at": i.last_seen_at,
        }
        for i in incidents
    ]


@router.get("/{incident_id}")
def get_incident_detail(incident_id: str, db: Session = Depends(get_db)):
    incident = db.query(Incident).filter(Incident.id == incident_id).first()

    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    explanations = (
        db.query(Explanation)
        .filter(Explanation.incident_id == incident.id)
        .order_by(Explanation.version.asc())
        .all()
    )

    return {
        "id": str(incident.id),
        "source_id": str(incident.source_id),
        "status": incident.status,
        "risk_level": incident.current_risk_level,
        "magnitude": incident.current_magnitude,
        "first_seen_at": incident.first_seen_at,
        "last_seen_at": incident.last_seen_at,
        "resolved_at": incident.resolved_at,
        "explanations": [
            {
                "id": str(e.id),
                "version": e.version,
                "content": e.content,
                "model": e.model,
                "created_at": e.created_at,
            }
            for e in explanations
        ],
    }


@router.post("/{incident_id}/ack")
def acknowledge_incident(incident_id: str, db: Session = Depends(get_db)):
    incident = db.query(Incident).filter(Incident.id == incident_id).first()

    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    incident.status = "ACKED"
    db.commit()

    return {"status": "ok", "message": "Incident acknowledged"}


@router.post("/{incident_id}/regenerate")
def regenerate_explanation(incident_id: str, db: Session = Depends(get_db)):
    incident = db.query(Incident).filter(Incident.id == incident_id).first()

    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    assessment = (
        db.query(RiskAssessment)
        .filter(RiskAssessment.drift_signal.has(source_id=incident.source_id))
        .order_by(RiskAssessment.created_at.desc())
        .first()
    )

    if not assessment:
        raise HTTPException(status_code=400, detail="No risk assessment found for incident")

    allowed = should_generate_explanation(db, assessment, incident)

    if not allowed:
        raise HTTPException(status_code=403, detail="Regeneration not allowed by policy")

    client = get_llm_client()
    explanation = generate_explanation(db, assessment, incident, client)

    return {
        "status": "ok",
        "explanation_id": str(explanation.id),
        "version": explanation.version,
    }
