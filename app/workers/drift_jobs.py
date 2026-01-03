from sqlalchemy.orm import Session

from app.core.baselines.first_snapshot import get_baseline_snapshot
from app.core.drift.compare import compute_drift
from app.core.drift.magnitude import compute_drift_magnitude
from app.core.models import Snapshot, DriftSignal, Incident
from app.core.drift.fingerprint import compute_drift_fingerprint
from app.core.risk.interpreter import interpret_risk

import logging

logger = logging.getLogger("driftline.drift")


def compute_and_store_drift(db: Session, source_id):
    baseline = get_baseline_snapshot(db, source_id)
    if not baseline:
        return None

    current = (
        db.query(Snapshot)
        .filter(Snapshot.source_id == source_id)
        .order_by(Snapshot.captured_at.desc())
        .first()
    )

    if baseline.id == current.id:
        # This snapshot *is* the baseline
        return None

    baseline_state = baseline.normalized_state.get("value", {})
    current_state = current.normalized_state.get("value", {})

    components = compute_drift(baseline_state, current_state)
    logger.debug(
        "Drift detected",
        extra={
            "source_id": source_id,
            "components": components,
        },
    )


    # 🔑 RESOLUTION: no drift detected => system back to baseline
    if not components:
        open_incidents = (
            db.query(Incident)
            .filter(Incident.source_id == source_id)
            .filter(Incident.status.in_(["OPEN", "ACKED"]))
            .all()
        )

        for incident in open_incidents:
            incident.status = "RESOLVED"
            incident.resolved_at = current.captured_at

        if open_incidents:
            db.commit()

        return None


    # 🔑 fingerprint only exists when drift exists
    fingerprint = compute_drift_fingerprint(components)

    magnitude = compute_drift_magnitude(components, baseline_state)

    incident = (
        db.query(Incident)
        .filter(Incident.source_id == source_id)
        .filter(Incident.drift_fingerprint == fingerprint)
        .filter(Incident.status != "RESOLVED")
        .first()
    )

    if incident:
        # Update existing incident
        incident.last_seen_at = current.captured_at
        incident.current_magnitude = magnitude
        incident.current_risk_level = interpret_risk(magnitude)
        db.commit()
        return None  # no new incident
    else:
        incident = Incident(
            source_id=source_id,
            drift_fingerprint=fingerprint,
            baseline_snapshot_id=baseline.id,
            first_seen_at=current.captured_at,
            last_seen_at=current.captured_at,
            status="OPEN",
            current_magnitude=magnitude,
            current_risk_level=interpret_risk(magnitude),
            origin="RUNTIME",
        )

        db.add(incident)
        db.commit()
        db.refresh(incident)
    

    signal = DriftSignal(
        source_id=source_id,
        baseline_snapshot_id=baseline.id,
        current_snapshot_id=current.id,
        component_count=len(components),
        magnitude=magnitude,
        components=components,
    )

    db.add(signal)
    db.commit()
    db.refresh(signal)

    return signal

