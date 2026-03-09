from __future__ import annotations

from pathlib import Path

from core.runtime.paths import find_repo_root
from core.vision.selector import choose_vision_path
from core.runtime.config import load_config
from core.vision.clarifier import load_clarification_session
from core.vision.models import VisionStatus, VisionLoadResult


# ---------------------------------------------------------
# Constants
# ---------------------------------------------------------

DEFAULT_VISION_FILENAME = "vision.md"


# ---------------------------------------------------------
# Core loader
# ---------------------------------------------------------

def find_vision_candidates() -> list[Path]:
    """
    Search repository for vision.md candidates.

    Strategy:
    - Prefer repo root
    - Then shallow recursive search
    - Ignore heavy/system directories
    """

    repo_root = find_repo_root()

    root_candidate = repo_root / DEFAULT_VISION_FILENAME
    candidates: list[Path] = []

    if root_candidate.exists():
        candidates.append(root_candidate)

    IGNORE_DIRS = {
        ".git",
        ".driftline",
        "node_modules",
        "venv",
        ".venv",
        "__pycache__",
    }

    for path in repo_root.rglob(DEFAULT_VISION_FILENAME):
        if path == root_candidate:
            continue

        if any(part in IGNORE_DIRS for part in path.parts):
            continue

        candidates.append(path)

    return candidates


def load_vision() -> VisionLoadResult:
    """
    Pure vision loader.

    No side effects.
    No LLM.
    No DB.
    """

    config = load_config()
    path: Path | None = None

    # -----------------------------------------------------
    # 1) Use configured vision path if valid
    # -----------------------------------------------------
    if config.vision_path:
        configured_path = Path(config.vision_path)
        if configured_path.exists():
            path = configured_path

    # -----------------------------------------------------
    # 2) Discover candidates if needed
    # -----------------------------------------------------
    if path is None:
        candidates = find_vision_candidates()

        if not candidates:
            return VisionLoadResult(
                status=VisionStatus.MISSING,
                path=None,
                raw_text=None,
                needs_clarification=True,
            )

        if len(candidates) == 1:
            path = candidates[0]
        else:
            path = choose_vision_path(candidates)

    # -----------------------------------------------------
    # 3) Read safely
    # -----------------------------------------------------
    try:
        raw_text = path.read_text(encoding="utf-8")
    except Exception:
        return VisionLoadResult(
            status=VisionStatus.EMPTY,
            path=path,
            raw_text=None,
            needs_clarification=False,
        )

    # -----------------------------------------------------
    # 4) Clarification state
    # -----------------------------------------------------

    session = load_clarification_session()

    needs_clarification = (
        session is None or session.status == "pending"
    )

    return VisionLoadResult(
        status=VisionStatus.FOUND,
        path=path,
        raw_text=raw_text,
        needs_clarification=needs_clarification,
    )