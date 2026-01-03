import json
import yaml


def normalize_content(raw: str) -> dict:
    """
    Attempt structured normalization.
    Falls back to raw text.
    """
    try:
        return {"type": "json", "value": json.loads(raw)}
    except Exception:
        pass

    try:
        return {"type": "yaml", "value": yaml.safe_load(raw)}
    except Exception:
        pass

    return {"type": "text", "value": raw.strip()}
