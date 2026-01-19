import logging
from sqlalchemy.orm import Session

from app.core.models import RiskAssessment, Explanation, Incident
from app.core.risk.tiers import risk_tier

logger = logging.getLogger(__name__)

EXPLANATION_TIER_MAP = {
    "LOW": "FREE",
    "MODERATE": "PRO",
    "HIGH": "ENTERPRISE",
}

def should_generate_explanation(db: Session, assessment: RiskAssessment, incident: Incident) -> bool:
    if incident.status in ("ACKED", "RESOLVED"):
        return False

    org = incident.org
    if not org:
        return False

    # FREE plan never regenerates
    if org.plan == "FREE":
        return incident.last_explained_tier is None

    prev_tier = incident.last_explained_tier
    curr_tier = risk_tier(assessment.magnitude)

    if not prev_tier:
        return True

    return curr_tier > prev_tier

