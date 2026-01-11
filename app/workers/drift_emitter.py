from sqlalchemy.orm import Session

from app.core.models import Snapshot, DriftSignal
from app.core.diffing.structured_diff import diff_structured
from app.core.drift.fingerprint import compute_drift_fingerprint
from app.core.drift.magnitude import compute_drift_magnitude
from app.core.baselines.first_snapshot import get_baseline_snapshot


def emit_drift_signal(db: Session, snapshot: Snapshot) -> DriftSignal | None:
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

    return signal
