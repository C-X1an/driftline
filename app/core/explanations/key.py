import hashlib


def compute_explanation_key(incident_id: str) -> str:
    return hashlib.sha256(incident_id.encode()).hexdigest()

