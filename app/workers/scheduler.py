import time
import logging
from datetime import datetime, timezone

from app.db.session import SessionLocal
from app.core.models import Source, Incident, Snapshot
from app.workers.snapshot_jobs import capture_snapshot
from app.workers.explanation_policy import should_generate_explanation
from app.workers.explanation_jobs import generate_explanation
from app.llm.mock import MockLLMClient  # swap later
from app.workers.drift_jobs import compute_and_store_drift
from app.workers.risk_jobs import compute_and_store_risk



logging.basicConfig(
    level=logging.DEBUG,
    format="%(levelname)s:%(name)s:%(message)s",
)
logger = logging.getLogger("driftline.scheduler")


POLL_INTERVAL_SECONDS = 30  # v1 default


def run_scheduler():
    logger.info("Driftline scheduler started")

    while True:
        db = SessionLocal()
        try:
            sources = (
                db.query(Source)
                .filter(Source.active.is_(True))
                .all()
            )

            logger.info("Found %d active sources", len(sources))

            for source in sources:
                try:
                    # 0. Initialize monitoring start time ONCE
                    if not source.monitoring_started_at:
                        source.monitoring_started_at = datetime.now(timezone.utc)
                        db.commit()

                    # 1. Capture snapshot (ALWAYS exactly once per cycle)
                    capture_snapshot(db, source)

                    # 1.5 Set baseline ONCE, on first snapshot after monitoring starts
                    if not db.query(Snapshot).filter(
                        Snapshot.source_id == source.id,
                        Snapshot.is_baseline.is_(True),
                    ).first():
                        baseline_snapshot = (
                            db.query(Snapshot)
                            .filter(Snapshot.source_id == source.id)
                            .order_by(Snapshot.captured_at.desc())
                            .first()
                        )

                        if baseline_snapshot:
                            baseline_snapshot.is_baseline = True
                            db.commit()

                    # 2. Compute drift
                    signal = compute_and_store_drift(db, source.id)
                    if not signal:
                        continue

                    # 3. Compute risk
                    assessment = compute_and_store_risk(db, signal)

                    # 4. Explanation logic (unchanged)
                    incident = (
                        db.query(Incident)
                        .filter(Incident.source_id == source.id)
                        .filter(Incident.status != "RESOLVED")
                        .order_by(Incident.last_seen_at.desc())
                        .first()
                    )

                    if should_generate_explanation(db, assessment, incident):
                        client = MockLLMClient()
                        generate_explanation(db, assessment, client)

                except Exception as e:
                    logger.exception(
                        "Snapshot failed for source %s: %s",
                        source.id,
                        e,
                    )
        finally:
            db.close()

        time.sleep(POLL_INTERVAL_SECONDS)
