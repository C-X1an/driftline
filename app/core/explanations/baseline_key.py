import hashlib

def compute_baseline_change_key(source_id: str) -> str:
    raw = f"baseline-reset:{source_id}"
    return hashlib.sha256(raw.encode()).hexdigest()
