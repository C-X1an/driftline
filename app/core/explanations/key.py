import hashlib


def compute_explanation_key(
    baseline_snapshot_id: str,
    drift_fingerprint: str,
    risk_level: str,
) -> str:
    raw = f"{baseline_snapshot_id}:{drift_fingerprint}:{risk_level}"
    return hashlib.sha256(raw.encode()).hexdigest()
