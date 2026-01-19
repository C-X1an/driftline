from sqlalchemy.orm import Session

from app.core.models import RiskAssessment, DriftSignal
from app.core.risk.interpreter import interpret_risk


def assess_risk(db: Session, signal: DriftSignal) -> RiskAssessment:
    """
    Deterministic risk assessment.
    Exactly ONE RiskAssessment per DriftSignal.
    """

    existing = (
        db.query(RiskAssessment)
        .filter(RiskAssessment.drift_signal_id == signal.id)
        .first()
    )

    if existing:
        return existing

    risk_level = interpret_risk(signal.magnitude)
    try:
        assessment = RiskAssessment(
            drift_signal_id=signal.id,
            risk_level=risk_level,
            magnitude=signal.magnitude,
        )

        db.add(assessment)
        db.commit()
        db.refresh(assessment)

        return assessment
    except Exception as e:
        print("💥 EXCEPTION IN assess_risk:", repr(e))
        raise
