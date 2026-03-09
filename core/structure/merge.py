from __future__ import annotations

from typing import Iterable, Dict, Tuple

from core.structure.models import StructuralGraph, Symbol, Dependency


# =========================================================
# Deterministic identity helpers
# =========================================================

def _symbol_key(symbol: Symbol) -> Tuple[str, str, str]:
    """
    Stable identity for deduplication.

    We assume:
    - same name
    - same type
    - same file path

    ⇒ represents same logical symbol across scans.
    """
    return (symbol.name, symbol.type, symbol.file_path)


def _dependency_key(dep: Dependency) -> Tuple[str, str, str]:
    """
    Stable identity for dependencies.
    """
    return (dep.source_id, dep.target_id, dep.type)


# =========================================================
# Merge logic
# =========================================================

def merge_structural_graphs(graphs: Iterable[StructuralGraph]) -> StructuralGraph:
    """
    Merge multiple per-file StructuralGraphs into one repo-level graph.

    Responsibilities:
    - deduplicate symbols deterministically
    - deduplicate dependencies
    - preserve repo_id from first graph
    """

    graphs = list(graphs)

    if not graphs:
        raise ValueError("No structural graphs provided for merge.")

    repo_id = graphs[0].repo_id
    merged = StructuralGraph(repo_id=repo_id)

    # -----------------------------------------
    # Deduplicate + enrich symbols (Option B)
    # -----------------------------------------
    seen_symbols: Dict[Tuple[str, str, str], Symbol] = {}


    def _merge_parameters(a: list[str], b: list[str]) -> list[str]:
        """
        Union parameters while preserving order from first appearance.
        """
        result = list(a)
        for p in b:
            if p not in result:
                result.append(p)
        return result


    def _choose_return_type(a: str | None, b: str | None) -> str | None:
        """
        Prefer richer return type deterministically.

        Priority:
        - non-None beats None
        - longer string considered more specific
        """
        if a is None:
            return b
        if b is None:
            return a

        return a if len(a) >= len(b) else b


    for graph in graphs:
        for symbol in graph.symbols:
            key = _symbol_key(symbol)

            if key not in seen_symbols:
                seen_symbols[key] = symbol
                merged.add_symbol(symbol)
                continue

            # ---------------------------------
            # Enrich existing symbol
            # ---------------------------------
            existing = seen_symbols[key]

            existing.parameters = _merge_parameters(
                existing.parameters,
                symbol.parameters,
            )

            existing.return_type = _choose_return_type(
                existing.return_type,
                symbol.return_type,
            )

    # -----------------------------------------
    # Deduplicate dependencies
    # -----------------------------------------
    seen_deps: Dict[Tuple[str, str, str], Dependency] = {}

    for graph in graphs:
        for dep in graph.dependencies:
            key = _dependency_key(dep)

            if key not in seen_deps:
                seen_deps[key] = dep
                merged.add_dependency(dep)

    return merged