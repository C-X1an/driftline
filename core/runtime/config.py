from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List, Optional

from core.runtime.paths import get_driftline_dir


CONFIG_FILENAME = "config.json"


# ---------------------------------------------------------
# Data model
# ---------------------------------------------------------

@dataclass
class DriftlineConfig:
    """
    Persistent runtime configuration stored in .driftline/config.json
    """

    # Absolute path to chosen vision.md
    vision_path: Optional[str] = None

    # Glob-style ignore patterns
    ignore_paths: List[str] = None

    def __post_init__(self):
        if self.ignore_paths is None:
            self.ignore_paths = []


# ---------------------------------------------------------
# Paths
# ---------------------------------------------------------

def get_config_path() -> Path:
    """
    Returns .driftline/config.json path.
    """
    return get_driftline_dir() / CONFIG_FILENAME


# ---------------------------------------------------------
# Load / Save
# ---------------------------------------------------------

def load_config() -> DriftlineConfig:
    """
    Loads config.json if present.
    Otherwise returns default config (not saved yet).
    """

    path = get_config_path()

    if not path.exists():
        return DriftlineConfig()

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return DriftlineConfig(**data)
    except Exception:
        # Corrupt config → reset safely
        return DriftlineConfig()


def save_config(config: DriftlineConfig) -> None:
    """
    Persists config.json to disk.
    """

    path = get_config_path()

    path.write_text(
        json.dumps(asdict(config), indent=2),
        encoding="utf-8",
    )