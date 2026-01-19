from typing import Any, Dict, List


def diff_structured(old: Any, new: Any, path: str = "") -> List[Dict[str, Any]]:
    """
    Compute a deep, leaf-level diff between two structured objects.
    Each changed leaf = one component.
    Returns list of {path, before, after}
    """
    diffs: List[Dict[str, Any]] = []

    # Case 1: Type changed entirely
    if type(old) != type(new):
        diffs.append({
            "path": path,
            "before": old,
            "after": new,
        })
        return diffs

    # Case 2: Dict → recurse per key
    if isinstance(old, dict):
        old_keys = set(old.keys())
        new_keys = set(new.keys())

        # Added keys
        for key in new_keys - old_keys:
            new_path = f"{path}.{key}" if path else key
            diffs.append({
                "path": new_path,
                "before": None,
                "after": new[key],
            })

        # Removed keys
        for key in old_keys - new_keys:
            new_path = f"{path}.{key}" if path else key
            diffs.append({
                "path": new_path,
                "before": old[key],
                "after": None,
            })

        # Modified keys
        for key in old_keys & new_keys:
            new_path = f"{path}.{key}" if path else key
            diffs.extend(diff_structured(old[key], new[key], new_path))

        return diffs

    # Case 3: List → compare index by index
    if isinstance(old, list):
        max_len = max(len(old), len(new))

        for i in range(max_len):
            new_path = f"{path}[{i}]"
            if i >= len(old):
                diffs.append({
                    "path": new_path,
                    "before": None,
                    "after": new[i],
                })
            elif i >= len(new):
                diffs.append({
                    "path": new_path,
                    "before": old[i],
                    "after": None,
                })
            else:
                diffs.extend(diff_structured(old[i], new[i], new_path))

        return diffs

    # Case 4: Primitive → direct compare
    if old != new:
        diffs.append({
            "path": path,
            "before": old,
            "after": new,
        })

    return diffs
