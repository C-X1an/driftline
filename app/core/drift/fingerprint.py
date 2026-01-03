import hashlib
import json


def compute_drift_fingerprint(components: list[dict]) -> str:
    """
    Produces a stable hash for semantic drift.
    Order-independent.
    """
    normalized = [
        {
            "path": c["path"],
            "change_type": c["change_type"],
        }
        for c in components
    ]

    normalized.sort(key=lambda x: (x["path"], x["change_type"]))

    payload = json.dumps(normalized, separators=(",", ":"), sort_keys=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()
