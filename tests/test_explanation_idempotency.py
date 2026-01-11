import pytest
from sqlalchemy.orm import Session

from app.core.models import Source, Snapshot, Incident, Explanation
from app.workers.snapshot_jobs import capture_snapshot
from app.workers.explanation_jobs import generate_explanation_for_incident


def test_explanation_is_reused_for_identical_drift(db_session: Session):
    """
    Invariant: Identical drift conditions must reuse the same explanation.
    """

    # 1. Create source
    source = Source(name="test-source")
    db_session.add(source)
    db_session.commit()

    # 2. Capture baseline snapshot
    baseline_snapshot = capture_snapshot(db_session, source.id)
    source.baseline_snapshot_id = baseline_snapshot.id
    db_session.commit()

    # 3. Introduce drift
    # TODO: mutate system state here in the same way twice

    # 4. Capture drift snapshot
    drift_snapshot_1 = capture_snapshot(db_session, source.id)

    # 5. Trigger incident + explanation
    incident_1 = db_session.query(Incident).filter_by(source_id=source.id).first()
    explanation_1 = db_session.query(Explanation).first()

    # 6. Resolve incident
    incident_1.status = "RESOLVED"
    db_session.commit()

    # 7. Re-introduce identical drift
    # TODO: same mutation again

    # 8. Capture second drift snapshot
    drift_snapshot_2 = capture_snapshot(db_session, source.id)

    # 9. Trigger second incident
    incident_2 = db_session.query(Incident).filter(
        Incident.source_id == source.id,
        Incident.id != incident_1.id
    ).first()

    explanation_2 = db_session.query(Explanation).filter(
        Explanation.id == incident_2.explanation_id
    ).first()

    # 10. Assertions
    assert explanation_1.id == explanation_2.id, "Explanation should be reused, not regenerated"
