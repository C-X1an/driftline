from typing import List, Dict, Any


def compute_drift_magnitude(
    components: List[Dict[str, Any]],
    baseline_state: dict,
) -> float:
    """
    Compute normalized drift magnitude in range [0.0, 1.0+]
    """

    if not components:
        return 0.0

    # Base weight: number of changed components
    count_weight = len(components)

    # Depth weight: deeper paths are more significant
    depth_weight = 0
    for c in components:
        path = c.get("path", "")
        depth = path.count(".") + path.count("[")
        depth_weight += depth

    raw_score = count_weight + (0.5 * depth_weight)

    # Normalize relative to baseline size if possible
    baseline_size = _estimate_structure_size(baseline_state)

    if baseline_size > 0:
        magnitude = raw_score / baseline_size
    else:
        magnitude = raw_score

    return round(float(magnitude), 4)


def _estimate_structure_size(obj) -> int:
    """
    Rough size estimate for normalization.
    """
    if isinstance(obj, dict):
        return sum(_estimate_structure_size(v) for v in obj.values()) + len(obj)
    if isinstance(obj, list):
        return sum(_estimate_structure_size(v) for v in obj) + len(obj)
    return 1
