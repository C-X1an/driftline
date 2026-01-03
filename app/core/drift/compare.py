from typing import Any, Dict, List


def compute_drift(
    baseline_state: Dict[str, Any],
    current_state: Dict[str, Any],
) -> List[Dict[str, Any]]:
    """
    Computes structural drift between two normalized states.

    Returns a list of drift components.
    """

    components: List[Dict[str, Any]] = []

    baseline_keys = set(baseline_state.keys())
    current_keys = set(current_state.keys())

    # Added keys
    for key in current_keys - baseline_keys:
        components.append({
            "path": key,
            "baseline": None,
            "current": current_state[key],
            "change_type": "added",
        })

    # Removed keys
    for key in baseline_keys - current_keys:
        components.append({
            "path": key,
            "baseline": baseline_state[key],
            "current": None,
            "change_type": "removed",
        })

    # Modified keys
    for key in baseline_keys & current_keys:
        if baseline_state[key] != current_state[key]:
            components.append({
                "path": key,
                "baseline": baseline_state[key],
                "current": current_state[key],
                "change_type": "modified",
            })

    return components
