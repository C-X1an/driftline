import uuid
from sqlalchemy.orm import Session

from app.core.models import Workspace, Source, Snapshot, Explanation
from app.workers.snapshot_jobs import capture_snapshot
from app.ingestion.registry import FETCHER_REGISTRY
from app.workers.explanation_jobs import generate_explanation
from app.core.models import RiskAssessment
from app.llm.mock import MockLLMClient


def test_explanation_is_reused_for_identical_drift(db: Session):
    """
    Invariant:
    Identical drift conditions MUST reuse the same explanation.
    No duplicate explanation rows allowed.
    """

    # --- Arrange workspace + source ---
    workspace = Workspace(
        id=uuid.uuid4(),
        name="test-workspace",
    )
    db.add(workspace)
    db.commit()

    source = Source(
        id=uuid.uuid4(),
        workspace_id=workspace.id,
        name="test-source",
        type="mock",
        active=True,
        fetch_spec={"type": "test_fetcher"},
        normalization_profile="default",
    )
    db.add(source)
    db.commit()

    # --- Mutable state for fetcher ---
    state = {"port": "1234"}

    def test_fetcher(_spec):
        return state

    FETCHER_REGISTRY["test_fetcher"] = test_fetcher

    llm_client = MockLLMClient()

    # --- 1. Capture baseline ---
    capture_snapshot(db, source)

    baseline_snapshot = (
        db.query(Snapshot)
        .filter(Snapshot.source_id == source.id)
        .order_by(Snapshot.captured_at.desc())
        .first()
    )
    baseline_snapshot.is_baseline = True
    db.commit()

    # --- 2. Introduce drift ---
    state["port"] = "5678"
    capture_snapshot(db, source)

    # At this point:
    # drift_emitter should have created DriftSignal + Incident + RiskAssessment

    assessment = db.query(RiskAssessment).first()
    assert assessment is not None, "RiskAssessment not created"

    explanation_1 = generate_explanation(db, assessment, llm_client)
    assert explanation_1 is not None

    explanation_count_after_first = db.query(Explanation).count()

    # --- 3. Resolve drift (back to baseline) ---
    state["port"] = "1234"
    capture_snapshot(db, source)

    # --- 4. Re-introduce IDENTICAL drift ---
    state["port"] = "5678"
    capture_snapshot(db, source)

    assessment_2 = (
        db.query(RiskAssessment)
        .order_by(RiskAssessment.created_at.desc())
        .first()
    )

    explanation_2 = generate_explanation(db, assessment_2, llm_client)

    explanation_count_after_second = db.query(Explanation).count()

    # --- Assertions ---
    assert explanation_1.id == explanation_2.id, "Explanation was regenerated instead of reused"
    assert explanation_count_after_first == explanation_count_after_second, "Duplicate explanation row created"
