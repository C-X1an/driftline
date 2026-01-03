from sqlalchemy.orm import Session

from app.core.models import DriftSignal, RiskAssessment
from app.core.risk.interpreter import interpret_risk


def compute_and_store_risk(db: Session, drift_signal: DriftSignal):
    # 1. Check if risk already exists for this signal
    existing = (
        db.query(RiskAssessment)
        .filter(RiskAssessment.drift_signal_id == drift_signal.id)
        .first()
    )
    if existing:
        return existing

    # 2. Compute risk only once per signal
    risk_level = interpret_risk(drift_signal.magnitude)

    assessment = RiskAssessment(
        drift_signal_id=drift_signal.id,
        risk_level=risk_level,
        magnitude=drift_signal.magnitude,
    )

    db.add(assessment)
    db.commit()
    db.refresh(assessment)

    return assessment

