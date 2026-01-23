from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func


from app.core.models import RiskAssessment, Snapshot, Incident, Explanation
from app.core.explanations.engine import generate_explanation as create_explanation
from app.llm.prompts import PROMPT_V1
from app.core.config import DEBUG_PIPELINE
from app.core.explanations.key import compute_explanation_key
from app.core.models.usage_event import UsageEvent
from app.core.risk.tiers import risk_tier

import logging

logger = logging.getLogger(__name__)

def generate_explanation(
    db: Session,
    assessment: RiskAssessment,
    incident: Incident,
    llm_client,
):
    if DEBUG_PIPELINE:
        print("🔥 assessment.id =", assessment.id)
        print("🔥 incident.id =", incident.id)

    try:
        baseline_snapshot = (
            db.query(Snapshot)
            .filter(
                Snapshot.source_id == assessment.drift_signal.source_id,
                Snapshot.is_baseline.is_(True),
            )
            .first()
        )
    except Exception as e:
        print("❌ EXCEPTION querying baseline_snapshot:", repr(e))
        raise

    if not baseline_snapshot:
        return None

    try:
        current_snapshot = (
            db.query(Snapshot)
            .filter(Snapshot.id == assessment.drift_signal.current_snapshot_id)
            .first()
        )
    except Exception as e:
        print("❌ EXCEPTION querying current_snapshot:", repr(e))
        raise

    if not current_snapshot:
        return None

    baseline_state = baseline_snapshot.normalized_state.get("value", {})
    current_state = current_snapshot.normalized_state.get("value", {})

    explanation_key = compute_explanation_key(str(incident.id))

    next_version = 1

    # 2. Idempotency guard (same version)
    max_version = (
        db.query(func.max(Explanation.version))
        .filter(Explanation.explanation_key == explanation_key)
        .scalar()
    )

    next_version = 1 if max_version is None else max_version + 1

    existing = (
        db.query(Explanation)
        .filter(
            Explanation.explanation_key == explanation_key,
            Explanation.version == next_version,
        )
        .first()
    )

    if existing:
        if DEBUG_PIPELINE:
            print("🔥 Explanation version already exists, skipping")
        return existing


    prompt = PROMPT_V1.format(
        risk_level=assessment.risk_level,
        magnitude=assessment.magnitude,
        components=assessment.drift_signal.components,
        baseline_state=baseline_state,
        current_state=current_state,
    )

    try:
        content = llm_client.generate(prompt)
    except Exception as e:
        print("❌ EXCEPTION during LLM generation:", repr(e))
        raise

    if DEBUG_PIPELINE:
        print("🔥 explanation_key =", explanation_key)
        print("🔥 next_version =", next_version)

    try:
        explanation = create_explanation(
            db=db,
            assessment=assessment,
            content=content,
            model=llm_client.model_name,
            prompt_version="v1",
            explanation_key=explanation_key,
            version=next_version,
            incident_id=incident.id,
        )
        incident.last_explained_tier = risk_tier(assessment.magnitude)
        db.add(incident)
    except Exception as e:
        print("❌ EXCEPTION during explanation insert:", repr(e))
        raise

    if incident.org.plan != "FREE":
        usage_event = UsageEvent(
            org_id=incident.org_id,
            event_type="EXPLANATION_GENERATED",
            quantity=1,
        )
        db.add(usage_event)

    db.commit()

    if DEBUG_PIPELINE:
        print("🔥 EXPLANATION CREATED, id =", explanation.id)

    logger.info(
        "billing.explanation.generated",
        extra={
            "org_id": incident.org_id,
            "incident_id": incident.id,
            "explanation_version": next_version,
            "risk_tier": risk_tier(assessment.magnitude),
        },
    )

    logger.info(
        "metric.explanation.generated",
        extra={
            "explanation_key": explanation_key,
            "version": next_version,
            "risk_assessment_id": assessment.id,
            "source_id": assessment.drift_signal.source_id,
        },
    )

    return explanation


