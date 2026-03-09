from __future__ import annotations
import os
import shutil
from pathlib import Path

# ---------------------------------------------------------
# Paths
# ---------------------------------------------------------

DRIFTLINE_DIR_NAME = ".driftline"


def find_repo_root(start: Path | None = None) -> Path:
    """
    Walk upward until we find a .git directory.
    That directory is considered the repository root.

    If no .git directory exists, fallback to the
    nearest directory (never a file).
    """

    current = start or Path.cwd()

    # Ensure we always start from a directory
    if current.is_file():
        current = current.parent

    for path in [current, *current.parents]:
        if (path / ".git").exists():
            return path

    # No .git found — fallback to top-level directory
    return current


def get_driftline_dir() -> Path:
    """
    Returns <repo-root>/.driftline
    """
    repo_root = find_repo_root()
    return repo_root / DRIFTLINE_DIR_NAME


def ensure_runtime_dirs() -> Path:
    """
    Creates .driftline directory if missing.
    Returns the path.
    """
    driftline_dir = get_driftline_dir()
    driftline_dir.mkdir(parents=True, exist_ok=True)
    return driftline_dir


def find_vscode_cli() -> str | None:
    # 1️⃣ Check PATH normally
    path = shutil.which("code")
    if path:
        return path

    # 2️⃣ Check common Windows locations
    possible_paths = [
        os.path.expandvars(r"%LocalAppData%\Programs\Microsoft VS Code\bin\code.cmd"),
        r"C:\Program Files\Microsoft VS Code\bin\code.cmd",
        r"C:\Program Files (x86)\Microsoft VS Code\bin\code.cmd",
    ]

    for p in possible_paths:
        if os.path.exists(p):
            return p

    return None