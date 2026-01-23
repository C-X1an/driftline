from dataclasses import dataclass
from typing import Optional


@dataclass
class ExplanationDecision:
    allowed: bool
    reason: Optional[str] = None

REASON_ACKED = "INCIDENT_NOT_OPEN"
REASON_FREE_LIMIT = "FREE_PLAN_LIMIT"
REASON_SAME_TIER = "SAME_TIER"
REASON_LIMIT_REACHED = "LIMIT_REACHED"
REASON_ALLOWED = None
