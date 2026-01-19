import hashlib
import json
from typing import Any


def _canonicalize(raw: Any) -> str:
    """
    Convert raw input into a deterministic string representation.
    Supports dict, list, and str.
    """
    if isinstance(raw, (dict, list)):
        # Deterministic JSON serialization (order-independent)
        return json.dumps(raw, sort_keys=True, separators=(",", ":"))
    elif isinstance(raw, str):
        return raw.replace("\r\n", "\n").strip()
    else:
        # Fallback: stringify
        return str(raw)


def fingerprint_raw_content(raw: Any) -> str:
    canonical = _canonicalize(raw)
    print("🔥 DEBUG CANONICAL RAW:", repr(canonical))
    return hashlib.sha256(canonical.encode()).hexdigest()

