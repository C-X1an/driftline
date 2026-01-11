import uuid
from sqlalchemy.orm import Session

from app.workers.snapshot_jobs import capture_snapshot
from app.core.models import Source, Snapshot, Workspace, SnapshotError
from app.ingestion.registry import FETCHER_REGISTRY


def test_snapshot_idempotency_no_duplicate_on_same_state(db: Session):
    """
    Invariant:
    If system state does not change, capture_snapshot must NOT create a new snapshot.
    """

    # --- Arrange ---
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

    state = {"port": "1234"}

    def test_fetcher(_spec):
        return state

    FETCHER_REGISTRY["test_fetcher"] = test_fetcher

    # --- Act 1 ---
    capture_snapshot(db, source)

    errors = db.query(SnapshotError).filter(SnapshotError.source_id == source.id).all()
    
    for err in errors:
        print("SnapshotError.type:", err.error_type)
        print("SnapshotError.message:", err.error_message)
    
    snapshots = db.query(Snapshot).filter(Snapshot.source_id == source.id).all()
    assert len(snapshots) == 1


    snapshots = db.query(Snapshot).filter(Snapshot.source_id == source.id).all()
    assert len(snapshots) == 1

    first_fingerprint = snapshots[0].raw_fingerprint

    # --- Act 2 (same state) ---
    capture_snapshot(db, source)

    snapshots = db.query(Snapshot).filter(Snapshot.source_id == source.id).all()
    assert len(snapshots) == 1, "Duplicate snapshot created despite no state change"
    assert snapshots[0].raw_fingerprint == first_fingerprint

def test_snapshot_creates_new_on_state_change(db: Session):
    """
    Invariant:
    If system state changes, capture_snapshot MUST create a new snapshot.
    """

    # --- Arrange ---
    workspace = Workspace(
        id=uuid.uuid4(),
        name="test-workspace-2",
    )
    db.add(workspace)
    db.commit()

    source = Source(
        id=uuid.uuid4(),
        workspace_id=workspace.id,
        name="test-source-2",
        type="mock",
        active=True,
        fetch_spec={"type": "test_fetcher_2"},
        normalization_profile="default",
    )
    db.add(source)
    db.commit()

    state = {"port": "1234"}

    def test_fetcher(_spec):
        return state

    FETCHER_REGISTRY["test_fetcher_2"] = test_fetcher

    # --- Act 1 ---
    capture_snapshot(db, source)

    snapshots = db.query(Snapshot).filter(Snapshot.source_id == source.id).all()
    assert len(snapshots) == 1

    # --- Mutate state ---
    state["port"] = "5678"

    # --- Act 2 ---
    capture_snapshot(db, source)

    snapshots = db.query(Snapshot).filter(Snapshot.source_id == source.id).order_by(Snapshot.captured_at).all()
    assert len(snapshots) == 2, "New snapshot not created after state change"

    assert snapshots[0].raw_fingerprint != snapshots[1].raw_fingerprint
