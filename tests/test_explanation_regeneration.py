import uuid
from datetime import datetime, timezone

from app.core.models import (
    Org,
    Source,
    Snapshot,
    Incident,
    Explanation,
    UsageEvent,
)
from app.core.explanations.policy import should_generate_explanation
from app.core.risk.tiers import risk_tier


def make_snapshot(source_id, state):
    return Snapshot(
        id=uuid.uuid4(),
        source_id=source_id,
        normalized_state={"value": state},
        created_at=datetime.now(timezone.utc),
    )


def test_explanation_regenerates_only_on_tier_escalation(db):
    """
    PRO plan behavior:

    - First explanation → allowed
    - Same tier drift → blocked
    - Higher tier drift → allowed
    - Lower tier drift → blocked

    Billing must match explanation count exactly.
    """

    # ------------------------------------------------------------------
    # 1. Org (PRO)
    # ------------------------------------------------------------------
    org = Org(
        id=uuid.uuid4(),
        name="Test PRO Org",
        plan="PRO",
    )
    db.add(org)
    db.commit()

    # ------------------------------------------------------------------
    # 2. Source
    # ------------------------------------------------------------------
    source = Source(
        id=uuid.uuid4(),
        name="config.yaml",
        type="CONFIG",
        fetch_spec={},
        normalization_profile="yaml",
        active=True,
        org_id=org.id,
        workspace_id=uuid.uuid4(),
    )
    db.add(source)
    db.commit()

    # ------------------------------------------------------------------
    # 3. Incident
    # ------------------------------------------------------------------
    incident = Incident(
        id=uuid.uuid4(),
        source_id=source.id,
        org_id=org.id,
        drift_fingerprint="fp-1",
        baseline_snapshot_id=uuid.uuid4(),
        status="OPEN",
        origin="RUNTIME",
        current_magnitude=0.10,
        current_risk_level=risk_tier(0.10),
        last_explained_tier=None,
        first_seen_at=datetime.now(timezone.utc),
        last_seen_at=datetime.now(timezone.utc),
    )
    db.add(incident)
    db.commit()

    # ------------------------------------------------------------------
    # 4. First explanation (LOW)
    # ------------------------------------------------------------------
    class DummyAssessment:
        magnitude = 0.10
        risk_level = risk_tier(0.10)

    assessment = DummyAssessment()

    assert should_generate_explanation(db, assessment, incident) is True

    incident.last_explained_tier = risk_tier(0.10)

    explanation_1 = Explanation(
        id=uuid.uuid4(),
        incident_id=incident.id,
        explanation_key="k",
        version=1,
        content="low risk explanation",
        model="mock",
        prompt_version="v1",
    )
    db.add(explanation_1)
    db.add(
        UsageEvent(
            org_id=org.id,
            event_type="EXPLANATION_GENERATED",
            quantity=1,
        )
    )
    db.commit()

    # ------------------------------------------------------------------
    # 5. Same tier again → BLOCKED
    # ------------------------------------------------------------------
    assessment.magnitude = 0.15  # still LOW

    assert should_generate_explanation(db, assessment, incident) is False

    # ------------------------------------------------------------------
    # 6. Escalation → MODERATE → ALLOWED
    # ------------------------------------------------------------------
    assessment.magnitude = 0.40

    assert should_generate_explanation(db, assessment, incident) is True

    incident.last_explained_tier = risk_tier(0.40)

    explanation_2 = Explanation(
        id=uuid.uuid4(),
        incident_id=incident.id,
        explanation_key="k",
        version=2,
        content="moderate risk explanation",
        model="mock",
        prompt_version="v1",
    )
    db.add(explanation_2)
    db.add(
        UsageEvent(
            org_id=org.id,
            event_type="EXPLANATION_GENERATED",
            quantity=1,
        )
    )
    db.commit()

    # ------------------------------------------------------------------
    # 7. Lower tier again → BLOCKED
    # ------------------------------------------------------------------
    assessment.magnitude = 0.20

    assert should_generate_explanation(db, assessment, incident) is False

    # ------------------------------------------------------------------
    # 8. Final assertions
    # ------------------------------------------------------------------
    explanations = (
        db.query(Explanation)
        .filter(Explanation.incident_id == incident.id)
        .order_by(Explanation.version)
        .all()
    )

    usage_events = (
        db.query(UsageEvent)
        .filter(UsageEvent.org_id == org.id)
        .all()
    )

    assert len(explanations) == 2
    assert explanations[0].version == 1
    assert explanations[1].version == 2

    assert len(usage_events) == 2
