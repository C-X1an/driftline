from typing import Any, Dict, List


def diff_structured(old: Any, new: Any, path: str = "") -> List[Dict[str, Any]]:
    """
    Compute a deep diff between two structured objects.
    Returns list of {path, before, after}
    """
    diffs = []

    if type(old) != type(new):
        diffs.append({
            "path": path,
            "before": old,
            "after": new,
        })
        return diffs

    if isinstance(old, dict):
        all_keys = set(old.keys()) | set(new.keys())
        for key in all_keys:
            new_path = f"{path}.{key}" if path else key
            if key not in old:
                diffs.append({"path": new_path, "before": None, "after": new[key]})
            elif key not in new:
                diffs.append({"path": new_path, "before": old[key], "after": None})
            else:
                diffs.extend(diff_structured(old[key], new[key], new_path))

    elif isinstance(old, list):
        min_len = min(len(old), len(new))
        for i in range(min_len):
            new_path = f"{path}[{i}]"
            diffs.extend(diff_structured(old[i], new[i], new_path))
        if len(old) != len(new):
            diffs.append({
                "path": path,
                "before": old,
                "after": new,
            })

    else:
        if old != new:
            diffs.append({
                "path": path,
                "before": old,
                "after": new,
            })

    return diffs
