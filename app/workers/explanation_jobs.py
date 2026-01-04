from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError


from app.core.models import RiskAssessment, Explanation, Snapshot, Incident
from app.llm.prompts import PROMPT_V1
from app.core.explanations.key import compute_explanation_key

import logging

logger = logging.getLogger(__name__)

def generate_explanation(
    db: Session,
    assessment: RiskAssessment,
    llm_client,
):
    baseline_snapshot = (
        db.query(Snapshot)
        .filter(
            Snapshot.source_id == assessment.drift_signal.source_id,
            Snapshot.is_baseline.is_(True),
        )
        .first()
    )

    if not baseline_snapshot:
        # Safety guard: no explanation without a baseline
        return None
    
    baseline_state = baseline_snapshot.normalized_state.get("value", {})
    current_snapshot = (
        db.query(Snapshot)
        .filter(Snapshot.id == assessment.drift_signal.current_snapshot_id)
        .first()
    )

    if not current_snapshot:
        # Safety guard: signal exists but snapshot missing
        return None

    current_state = current_snapshot.normalized_state.get("value", {})

    explanation_key = compute_explanation_key(
        baseline_snapshot_id=str(baseline_snapshot.id),
        drift_fingerprint=assessment.drift_signal.drift_fingerprint,
        risk_level=assessment.risk_level,
    )

    # Check cache (IMPORTANT)
    existing = (
        db.query(Explanation)
        .filter(Explanation.explanation_key == explanation_key)
        .first()
    )

    if existing:
        logger.info(
            "metric.explanation.reused",
            extra={
                "explanation_key": explanation_key,
                "risk_assessment_id": assessment.id,
                "source_id": assessment.drift_signal.source_id,
            },
        )
        return existing

    prompt = PROMPT_V1.format(
        risk_level=assessment.risk_level,
        magnitude=assessment.magnitude,
        components=assessment.drift_signal.components,
        baseline_state=baseline_state,
        current_state=current_state,
    )

    content = llm_client.generate(prompt)

    explanation = Explanation(
        risk_assessment_id=assessment.id,
        explanation_key=explanation_key,
        content=content,
        model=llm_client.model_name,
        prompt_version="v1",
    )

    logger.info(
        "metric.explanation.generated",
        extra={
            "explanation_key": explanation_key,
            "risk_assessment_id": assessment.id,
            "source_id": assessment.drift_signal.source_id,
        },
    )

    db.add(explanation)

    try:
        db.flush()
    except IntegrityError:
        db.rollback()
        return (
            db.query(Explanation)
            .filter(Explanation.explanation_key == explanation_key)
            .first()
        )

    incident = (
        db.query(Incident)
        .filter(
            Incident.source_id == assessment.drift_signal.source_id,
            Incident.drift_fingerprint == assessment.drift_signal.drift_fingerprint,
            Incident.status != "RESOLVED",
        )
        .order_by(Incident.first_seen_at.desc())
        .first()
    )

    if incident and incident.explanation_id is None:
        incident.explanation_id = explanation.id

    db.commit()
    db.refresh(explanation)

    return explanation

