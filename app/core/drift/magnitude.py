from typing import List, Dict, Any


def compute_drift_magnitude(
    components: List[Dict[str, Any]],
    baseline_state: Dict[str, Any],
) -> float:
    if not baseline_state:
        return 0.0

    return len(components) / max(len(baseline_state), 1)
