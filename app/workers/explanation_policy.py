from sqlalchemy.orm import Session

from app.core.models import RiskAssessment, Explanation, Incident
from app.core.risk.tiers import risk_tier


def should_generate_explanation(
    db: Session,
    assessment: RiskAssessment,
    incident: Incident,
) -> bool:
    
    # Do not generate explanations for ACKED incidents
    if incident and incident.status == "ACKED":
        return False
    
    # Case 1: no explanation yet
    existing = (
        db.query(Explanation)
        .filter(Explanation.risk_assessment_id == assessment.id)
        .first()
    )
    if not existing:
        return True

    # Case 2: compare with previous assessment
    previous = (
        db.query(RiskAssessment)
        .filter(
            RiskAssessment.drift_signal.has(
                source_id=assessment.drift_signal.source_id
            ),
            RiskAssessment.created_at < assessment.created_at,
        )
        .order_by(RiskAssessment.created_at.desc())
        .first()
    )

    if not previous:
        return False

    if previous.risk_level != assessment.risk_level:
        return True

    if risk_tier(previous.magnitude) != risk_tier(assessment.magnitude):
        return True

    return False
