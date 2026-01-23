import uuid

def test_free_plan_hits_explanation_limit(db):
    """
    FREE plan:
    - allows first explanation
    - blocks regeneration even on tier escalation
    """

    from app.core.models import Org, Incident, UsageEvent
    from app.core.explanations.policy import should_generate_explanation
    from app.core.risk.assessor import RiskAssessment
    from app.core.risk.tiers import risk_tier

    # org on FREE plan
    org = Org(name="Free Org", plan="FREE")
    db.add(org)
    db.commit()
    db.refresh(org)

    incident = Incident(
        org_id=org.id,
        source_id=uuid.UUID("00000000-0000-0000-0000-000000000001"),
        baseline_snapshot_id=uuid.UUID("00000000-0000-0000-0000-000000000002"),
        drift_fingerprint="abc",
        current_magnitude=0.2,
        current_risk_level="LOW",
        last_explained_tier="LOW",
    )

    db.add(incident)
    db.commit()
    
    # simulate tier escalation
    assessment = RiskAssessment(
        magnitude=0.9,
        risk_level="HIGH",
    )

    allowed = should_generate_explanation(db, assessment, incident)

    assert allowed is False
