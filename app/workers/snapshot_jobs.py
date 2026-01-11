from sqlalchemy.orm import Session

from app.core.models import Snapshot, SnapshotError, Source
from app.core.normalization.fingerprint import fingerprint_raw_content
from app.core.normalization.basic import normalize_content
from app.ingestion.registry import FETCHER_REGISTRY
from app.core.diffing.structured_diff import diff_structured
from app.workers.drift_emitter import emit_drift_signal




SCHEMA_VERSION = 1


def capture_snapshot(db: Session, source: Source) -> None:
    try:
        fetcher_type = source.fetch_spec.get("type")
        fetcher = FETCHER_REGISTRY.get(fetcher_type)

        if not fetcher:
            raise ValueError(f"Unsupported fetcher type: {fetcher_type}")

        raw_content = fetcher(source.fetch_spec)
        fingerprint = fingerprint_raw_content(raw_content)

        # Check last snapshot
        last_snapshot = (
            db.query(Snapshot)
            .filter(Snapshot.source_id == source.id)
            .order_by(Snapshot.captured_at.desc())
            .first()
        )

        if last_snapshot and last_snapshot.raw_fingerprint == fingerprint:
            # No state change — do nothing
            return

        normalized = normalize_content(raw_content)

        diff = None
        if last_snapshot:
            diff = diff_structured(
                last_snapshot.normalized_state.get("value"),
                normalized.get("value"),
            )

        snapshot = Snapshot(
            source_id=source.id,
            raw_fingerprint=fingerprint,
            normalized_state=normalized,
            diff=diff,
            schema_version=SCHEMA_VERSION,
        )

        db.add(snapshot)
        db.commit()
        emit_drift_signal(db, snapshot)

    except Exception as e:
        error = SnapshotError(
            source_id=source.id,
            error_type=type(e).__name__,
            error_message=str(e),
        )
        db.add(error)
        db.commit()
