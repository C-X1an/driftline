from __future__ import annotations

from pathlib import Path
from typing import List
import os

from core.runtime.paths import find_repo_root
from core.runtime.config import load_config
from core.structure.models import StructuralGraph, LanguageParser
from core.structure.merge import merge_structural_graphs

# Python parser (first supported language)
from core.structure.parsers.python_parser import PythonParser


# =========================================================
# Parser registry
# =========================================================

PARSERS: List[LanguageParser] = [
    PythonParser(),
]


# =========================================================
# Helpers
# =========================================================

def _is_ignored(path: Path, ignore_patterns: List[str]) -> bool:
    """
    Check whether a file path matches any ignore glob pattern.
    """
    for pattern in ignore_patterns:
        if path.match(pattern):
            return True
    return False


def _select_parser(file_path: Path) -> LanguageParser | None:
    """
    Return the first parser that can handle the file.
    """
    for parser in PARSERS:
        if parser.can_parse(file_path):
            return parser
    return None


# =========================================================
# Main scan entry
# =========================================================

def scan_repository() -> StructuralGraph:
    """
    Perform full structural scan of repository.

    Steps:
    1. Discover repo root
    2. Load ignore config
    3. Parse each file with correct language parser
    4. Create placeholder graphs for unsupported files (Option B)
    5. Merge into single repo StructuralGraph
    """

    repo_root = find_repo_root()
    config = load_config()

    per_file_graphs: List[StructuralGraph] = []

    # -----------------------------------------------------
    # Walk all files
    # -----------------------------------------------------
    for root, dirs, files in os.walk(repo_root):
        root_path = Path(root)

        # prune ignored directories
        dirs[:] = [
            d for d in dirs
            if not _is_ignored((root_path / d).relative_to(repo_root), config.ignore_paths)
        ]

        for file in files:
            path = root_path / file

            if _is_ignored(path.relative_to(repo_root), config.ignore_paths):
                continue

            # -------------------------------------------------
            # Select parser
            # -------------------------------------------------
            parser = _select_parser(path)

            if parser:
                try:
                    graph = parser.parse_file(path)
                    per_file_graphs.append(graph)
                except Exception:
                    # Never crash scan — return empty structural graph
                    per_file_graphs.append(
                        StructuralGraph(repo_id=str(repo_root))
                    )

            else:
                # -------------------------------------------------
                # Option B: unknown language → file-level placeholder symbol
                # -------------------------------------------------
                placeholder = StructuralGraph(repo_id=str(repo_root))

                from core.structure.models import Symbol

                placeholder.add_symbol(
                    Symbol(
                        id=str(path),
                        name=path.name,
                        type="file",
                        file_path=str(path),
                    )
                )

                per_file_graphs.append(placeholder)

    # -----------------------------------------------------
    # Merge all graphs → repo-level structural truth
    # -----------------------------------------------------
    if not per_file_graphs:
        return StructuralGraph(repo_id=str(repo_root))

    return merge_structural_graphs(per_file_graphs)