from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.core.models import (
    Source,
    DriftSignal,
    RiskAssessment,
    Explanation,
)

router = APIRouter(prefix="/sources", tags=["status"])


@router.get("/{source_id}/status")
def get_source_status(source_id: str, db: Session = Depends(get_db)):
    source = db.query(Source).filter(Source.id == source_id).first()
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")

    signal = (
        db.query(DriftSignal)
        .filter(DriftSignal.source_id == source.id)
        .order_by(DriftSignal.computed_at.desc())
        .first()
    )

    if not signal:
        return {
            "source_id": source_id,
            "status": "NO_DATA",
        }

    risk = (
        db.query(RiskAssessment)
        .filter(RiskAssessment.drift_signal_id == signal.id)
        .first()
    )

    explanation = None
    if risk:
        explanation = (
            db.query(Explanation)
            .filter(Explanation.risk_assessment_id == risk.id)
            .order_by(Explanation.created_at.desc())
            .first()
        )

    return {
        "source_id": source_id,
        "risk_level": risk.risk_level if risk else "UNKNOWN",
        "magnitude": signal.magnitude,
        "component_count": signal.component_count,
        "components": signal.components,
        "computed_at": signal.computed_at,
        "explanation": explanation.content if explanation else None,
    }
