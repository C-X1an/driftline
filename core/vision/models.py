
from dataclasses import dataclass
from enum import Enum
from pathlib import Path


# ---------------------------------------------------------
# Enums
# ---------------------------------------------------------

class VisionStatus(str, Enum):
    FOUND = "FOUND"
    MISSING = "MISSING"
    EMPTY = "EMPTY"


# ---------------------------------------------------------
# Result model
# ---------------------------------------------------------

@dataclass
class VisionLoadResult:
    status: VisionStatus
    path: Path | None
    raw_text: str | None
    needs_clarification: bool