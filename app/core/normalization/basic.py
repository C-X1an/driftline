import json
import yaml
from typing import Any


def normalize_content(raw: Any) -> dict:
    """
    Normalize raw content into structured form.
    Supports dict, list, JSON, YAML, and text.
    """

    # --- Structured input (preferred path) ---
    if isinstance(raw, (dict, list)):
        return {
            "type": "structured",
            "value": raw,
        }

    # --- String input ---
    if isinstance(raw, str):
        stripped = raw.strip()

        try:
            return {"type": "json", "value": json.loads(stripped)}
        except Exception:
            pass

        try:
            return {"type": "yaml", "value": yaml.safe_load(stripped)}
        except Exception:
            pass

        return {"type": "text", "value": stripped}

    # --- Fallback ---
    return {
        "type": "unknown",
        "value": str(raw),
    }
