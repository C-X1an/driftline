import logging
from sqlalchemy.orm import Session

from app.core.models import RiskAssessment, Explanation, Incident
from app.core.billing.limits import is_within_limit
from app.core.risk.tiers import risk_tier
from app.core.explanations.decision import (
    ExplanationDecision,
    REASON_ACKED,
    REASON_FREE_LIMIT,
    REASON_SAME_TIER,
    REASON_LIMIT_REACHED,
)

logger = logging.getLogger(__name__)

EXPLANATION_TIER_MAP = {
    "LOW": "FREE",
    "MODERATE": "PRO",
    "HIGH": "ENTERPRISE",
}

def should_generate_explanation(
    db: Session,
    assessment: RiskAssessment,
    incident: Incident,
) -> ExplanationDecision:

    if incident.status in ("ACKED", "RESOLVED"):
        return ExplanationDecision(
            allowed=False,
            reason=REASON_ACKED,
        )

    org = incident.org
    if not org:
        return ExplanationDecision(False)

    # FREE plan logic
    if org.plan == "FREE":
        if incident.last_explained_tier is None:
            return ExplanationDecision(True)
        return ExplanationDecision(
            allowed=False,
            reason=REASON_FREE_LIMIT,
        )

    prev_tier = incident.last_explained_tier
    curr_tier = risk_tier(assessment.magnitude)

    if not prev_tier:
        return ExplanationDecision(True)

    if curr_tier <= prev_tier:
        return ExplanationDecision(
            allowed=False,
            reason=REASON_SAME_TIER,
        )

    if not is_within_limit(
        db=db,
        org=org,
        event_type="EXPLANATION_GENERATED",
    ):
        return ExplanationDecision(
            allowed=False,
            reason=REASON_LIMIT_REACHED,
        )

    return ExplanationDecision(True)
