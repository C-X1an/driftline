import hashlib
import json
from typing import List, Dict, Any


def compute_drift_fingerprint(components: List[Dict[str, Any]]) -> str:
    """
    Deterministic fingerprint of drift components.
    Two semantically identical drifts MUST produce the same fingerprint.
    """

    # Sort components by path for stability
    canonical = sorted(
        components,
        key=lambda c: c.get("path", "")
    )

    payload = json.dumps(canonical, sort_keys=True, separators=(",", ":"))

    return hashlib.sha256(payload.encode("utf-8")).hexdigest()
