from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Protocol


# =========================================================
# Structural graph primitives
# =========================================================

@dataclass
class Symbol:
    """
    Represents a code symbol such as:

    - function
    - class
    - method
    - variable (optional later)

    This is LANGUAGE-AGNOSTIC.
    """
    id: str
    name: str
    type: str            # function | class | method | module | etc.
    file_path: str

    parameters: List[str] = field(default_factory=list)
    return_type: str | None = None


def _serialize_symbols(symbols: List[Symbol]) -> List[dict]:

    return sorted(
        [
            {
                "id": s.id,
                "name": s.name,
                "type": s.type,
                "file_path": s.file_path,
                "parameters": s.parameters,
                "return_type": s.return_type,
            }
            for s in symbols
        ],
        key=lambda x: x["id"],
    )



@dataclass
class Dependency:
    """
    Represents a directed relationship between symbols.

    Examples:
    - function A calls function B
    - class depends on module
    - file imports module
    """
    source_id: str
    target_id: str
    type: str            # calls | imports | inherits | uses | etc.

    def __post_init__(self):
        self.key = f"{self.source_id}|{self.type}|{self.target_id}"


def _serialize_dependencies(deps: List[Dependency]) -> List[dict]:

    return sorted(
        [
            {
                "source_id": d.source_id,
                "target_id": d.target_id,
                "type": d.type,
                "key": d.key,
            }
            for d in deps
        ],
        key=lambda x: x["key"],
    )


@dataclass
class StructuralGraph:
    """
    Raw structural truth extracted from repository.

    This feeds directly into PMM builder.
    """
    repo_id: str
    symbols: List[Symbol] = field(default_factory=list)
    dependencies: List[Dependency] = field(default_factory=list)

    # -----------------------------------------------------
    # Convenience helpers
    # -----------------------------------------------------

    def add_symbol(self, symbol: Symbol) -> None:
        self.symbols.append(symbol)

    def add_dependency(self, dep: Dependency) -> None:
        self.dependencies.append(dep)


# =========================================================
# Parser contract
# =========================================================

class LanguageParser(Protocol):
    """
    Universal parser interface.

    Every language-specific parser MUST implement this.
    """

    language: str

    def can_parse(self, file_path: Path) -> bool:
        """
        Return True if this parser supports the file.
        """
        ...

    def parse_file(self, file_path: Path) -> StructuralGraph:
        """
        Extract structural information from a single file.

        Must NEVER raise fatal errors.
        Should return empty graph on failure.
        """
        ...