from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session

from app.core.models import Incident, DriftSignal
from app.core.risk.interpreter import interpret_risk
from app.core.models.source import Source
from app.core.config import DEBUG_PIPELINE


INCIDENT_MERGE_WINDOW = timedelta(minutes=2)
AUTO_RESOLVE_AFTER = timedelta(minutes=15)
REOPEN_WINDOW = timedelta(minutes=30)


def handle_incident_lifecycle(db: Session, signal: DriftSignal):
    if DEBUG_PIPELINE:
        print("🔥 ENTER handle_incident_lifecycle")
        print("🔥 signal.source_id =", signal.source_id)
        print("🔥 signal.drift_fingerprint =", signal.drift_fingerprint)
        print("🔥 signal.magnitude =", signal.magnitude)

    now = datetime.now(timezone.utc)

    # 1. Try merge with recent OPEN/ACKED
    if DEBUG_PIPELINE:
        print("🔥 Checking merge_candidate...")

    merge_candidate = (
        db.query(Incident)
        .filter(
            Incident.source_id == signal.source_id,
            Incident.status.in_(["OPEN", "ACKED"]),
            Incident.last_seen_at >= (now - INCIDENT_MERGE_WINDOW),
        )
        .order_by(Incident.last_seen_at.desc())
        .first()
    )

    if merge_candidate:
        merge_candidate.last_seen_at = now

        new_risk = interpret_risk(signal.magnitude)
        existing_risk = merge_candidate.current_risk_level

        # Escalate only, never downgrade
        if _severity_rank(new_risk) > _severity_rank(existing_risk):
            merge_candidate.current_risk_level = new_risk
            merge_candidate.current_magnitude = signal.magnitude
        else:
            # still track magnitude for observability, but do not downgrade severity
            merge_candidate.current_magnitude = max(
                merge_candidate.current_magnitude,
                signal.magnitude,
            )

        db.commit()
        return merge_candidate

    # 2. Try reopen recently resolved same drift
    if DEBUG_PIPELINE:
        print("🔥 Checking reopen_candidate...")

    reopen_candidate = (
        db.query(Incident)
        .filter(
            Incident.source_id == signal.source_id,
            Incident.drift_fingerprint == signal.drift_fingerprint,
            Incident.status == "RESOLVED",
            Incident.resolved_at >= (now - REOPEN_WINDOW),
        )
        .order_by(Incident.resolved_at.desc())
        .first()
    )

    if reopen_candidate:
        reopen_candidate.status = "OPEN"
        reopen_candidate.first_seen_at = now
        reopen_candidate.last_seen_at = now
        new_risk = interpret_risk(signal.magnitude)

        if _severity_rank(new_risk) > _severity_rank(reopen_candidate.current_risk_level):
            reopen_candidate.current_risk_level = new_risk

        reopen_candidate.current_magnitude = signal.magnitude
        reopen_candidate.resolved_at = None
        db.commit()
        return reopen_candidate

    # 3. Else: create new incident
    if DEBUG_PIPELINE:
        print("🔥 Creating NEW incident")
    
    source = db.query(Source).filter(Source.id == signal.source_id).first()

    if not source:
        raise RuntimeError(f"Source {signal.source_id} not found while creating incident")

    if not source.org_id:
        raise RuntimeError(f"Source {signal.source_id} has no org_id – cannot create incident")
    
    incident = Incident(
        source_id=signal.source_id,
        org_id=source.org_id,  # 🔥 CRITICAL FIX
        drift_fingerprint=signal.drift_fingerprint,
        baseline_snapshot_id=signal.baseline_snapshot_id,
        first_seen_at=now,
        last_seen_at=now,
        status="OPEN",
        current_magnitude=signal.magnitude,
        current_risk_level=interpret_risk(signal.magnitude),
        origin="RUNTIME",
    )

    db.add(incident)
    db.commit()
    db.refresh(incident)

    return incident


def auto_resolve_stale_incidents(db: Session, source_id):
    now = datetime.now(timezone.utc)

    stale = (
        db.query(Incident)
        .filter(
            Incident.source_id == source_id,
            Incident.status.in_(["OPEN", "ACKED"]),
            Incident.last_seen_at < (now - AUTO_RESOLVE_AFTER),
        )
        .all()
    )

    for incident in stale:
        incident.status = "RESOLVED"
        incident.resolved_at = now

    if stale:
        db.commit()

def _severity_rank(level: str) -> int:
    return {
        "LOW": 1,
        "MODERATE": 2,
        "HIGH": 3,
    }.get(level, 0)
