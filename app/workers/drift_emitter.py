from sqlalchemy.orm import Session
from datetime import datetime, timezone

from app.core.models import Snapshot, DriftSignal, Incident
from app.core.config import DEBUG_PIPELINE
from app.core.diffing.structured_diff import diff_structured
from app.core.drift.fingerprint import compute_drift_fingerprint
from app.core.drift.magnitude import compute_drift_magnitude
from app.core.baselines.first_snapshot import get_baseline_snapshot
from app.core.incidents.handler import handle_incident_lifecycle, auto_resolve_stale_incidents
from app.core.risk.assessor import assess_risk
from app.core.explanations.policy import should_generate_explanation
from app.workers.explanation_jobs import generate_explanation
from app.llm.client import get_llm_client

def emit_drift_signal(db: Session, snapshot: Snapshot) -> DriftSignal | None:
    if DEBUG_PIPELINE:
        print("🔥🔥🔥 ENTER emit_drift_signal TOP OF FUNCTION")
        print("🔥 ENTER emit_drift_signal")
        print("🔥 snapshot.id =", snapshot.id)
        print("🔥 snapshot.source_id =", snapshot.source_id)

    baseline = get_baseline_snapshot(db, snapshot.source_id)

    if baseline is None:
        snapshot.is_baseline = True
        db.commit()
        return None

    if baseline.id == snapshot.id:
        return None

    old = baseline.normalized_state.get("value", {})
    new = snapshot.normalized_state.get("value", {})

    components = diff_structured(old, new)

    if not components:
        # 🔥 Immediate resolve when drift disappears
        open_incidents = (
            db.query(Incident)
            .filter(
                Incident.source_id == snapshot.source_id,
                Incident.status.in_(["OPEN", "ACKED"]),
            )
            .all()
        )

        for incident in open_incidents:
            incident.status = "RESOLVED"
            incident.resolved_at = datetime.now(timezone.utc)

        if open_incidents:
            db.commit()

        return None

    fingerprint = compute_drift_fingerprint(components)
    magnitude = compute_drift_magnitude(components, old)
    
    existing = db.query(DriftSignal).filter(
        DriftSignal.current_snapshot_id == snapshot.id,
        DriftSignal.drift_fingerprint == fingerprint,
    ).first()

    if existing:
        return existing

    signal = DriftSignal(
        source_id=snapshot.source_id,
        baseline_snapshot_id=baseline.id,
        current_snapshot_id=snapshot.id,
        drift_fingerprint=fingerprint,
        component_count=len(components),
        magnitude=magnitude,
        components=components,
    )

    db.add(signal)
    db.commit()
    db.refresh(signal)

    # 🔥 capture previous incident state BEFORE mutation
    prev_magnitude = None

    existing_incident = (
        db.query(Incident)
        .filter(
            Incident.source_id == signal.source_id,
            Incident.status.in_(["OPEN", "ACKED"]),
        )
        .order_by(Incident.last_seen_at.desc())
        .first()
    )

    if existing_incident:
        prev_magnitude = existing_incident.current_magnitude


    incident = handle_incident_lifecycle(db, signal)

    assessment = assess_risk(db, signal)

    # attach previous magnitude for policy decision
    incident._prev_magnitude = prev_magnitude

    decision = should_generate_explanation(db, assessment, incident)

    if decision.allowed:
        client = get_llm_client()
        generate_explanation(db, assessment, incident, client)
    else:
        if DEBUG_PIPELINE:
            print(
                "🚫 Explanation blocked:",
                decision.reason,
            )

    if DEBUG_PIPELINE:
        print("🔥🔥🔥 EXIT emit_drift_signal BOTTOM OF FUNCTION")
    return signal

