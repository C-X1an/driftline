from typing import List, Dict, Any


def compute_drift_magnitude(
    components: List[Dict[str, Any]],
    baseline_state: Dict[str, Any],
) -> float:
    """
    Compute normalized drift magnitude.
    Magnitude is relative to baseline size (fixed reference).
    """

    if not components:
        return 0.0

    # 1. Each changed component counts as 1
    count_weight = len(components)

    # 2. Depth penalty (nested changes are riskier)
    depth_weight = 0
    for c in components:
        path = c.get("path", "")
        depth = path.count(".") + path.count("[")
        depth_weight += depth

    raw_score = count_weight + (0.5 * depth_weight)

    # 🔥 CRITICAL: baseline size must be frozen reference
    baseline_size = _estimate_structure_size(baseline_state)

    if baseline_size <= 0:
        return round(float(raw_score), 4)

    magnitude = raw_score / baseline_size

    return round(float(magnitude), 4)


def _estimate_structure_size(obj) -> int:
    if isinstance(obj, dict):
        return sum(_estimate_structure_size(v) for v in obj.values()) + len(obj)
    if isinstance(obj, list):
        return sum(_estimate_structure_size(v) for v in obj) + len(obj)
    return 1
