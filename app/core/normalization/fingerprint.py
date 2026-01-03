import hashlib


def fingerprint_raw_content(raw: str) -> str:
    """
    Deterministic fingerprint of raw content.
    """
    normalized = raw.replace("\r\n", "\n").strip()
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()
