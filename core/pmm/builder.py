from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Set
import json

from core.ai.runtime import run_reasoning
from core.structure.models import StructuralGraph, Symbol, Dependency, _serialize_symbols, _serialize_dependencies
from core.pmm.models import (
    ProjectMeaningModel,
    Capability,
    Guarantee,
)
from core.ai.prompts.prompt_engine import build_prompt



# =========================================================
# Public Entry
# =========================================================

def build_pmm(
    structural_graph: StructuralGraph,
    vision_text: str | None,
) -> ProjectMeaningModel:
    """
    Full PMM construction pipeline (V1).

    Always rebuilt from scratch.
    Fully synchronous.
    """

    modules = _partition_by_top_level(structural_graph)

    fragments = _extract_module_fragments(
        modules,
        structural_graph,
        vision_text,
    )

    reconciled = _reconcile_fragments(
        fragments,
        structural_graph,
        vision_text,
    )

    validated_capabilities = _validate_capabilities(
        reconciled.get("capabilities", []),
        structural_graph,
    )

    validated_guarantees = _validate_guarantees(
        reconciled.get("guarantees", []),
        structural_graph,
    )

    return ProjectMeaningModel(
        repo_id=structural_graph.repo_id,
        generated_at=datetime.now(timezone.utc),
        capabilities=validated_capabilities,
        guarantees=validated_guarantees,
    )


# =========================================================
# Partitioning
# =========================================================

def _partition_by_top_level(
    structural_graph: StructuralGraph,
) -> Dict[str, StructuralGraph]:

    repo_root = Path(structural_graph.repo_id)

    modules: Dict[str, StructuralGraph] = {}
    symbol_to_module: Dict[str, str] = {}

    # ------------------------------
    # Group symbols
    # ------------------------------

    for symbol in structural_graph.symbols:

        path = Path(symbol.file_path)
        relative = path.relative_to(repo_root)

        parts = relative.parts

        if len(parts) == 1:
            module_name = "__root__"
        else:
            module_name = parts[0]

        if module_name not in modules:
            modules[module_name] = StructuralGraph(
                repo_id=structural_graph.repo_id
            )

        modules[module_name].add_symbol(symbol)
        symbol_to_module[symbol.id] = module_name

    # ------------------------------
    # Assign dependencies
    # ------------------------------

    for dep in structural_graph.dependencies:

        module_name = symbol_to_module.get(dep.source_id)
        if module_name is None:
            continue

        modules[module_name].add_dependency(dep)

    return modules


# =========================================================
# Module Extraction (Synchronous)
# =========================================================

def _extract_module_fragments(
    modules: Dict[str, StructuralGraph],
    structural_graph: StructuralGraph,
    vision_text: str | None,
) -> List[dict]:

    fragments: List[dict] = []

    for module_name, graph in modules.items():

        payload = {
            "module_name": module_name,
            "symbols": _serialize_symbols(graph.symbols),
            "dependencies": _serialize_dependencies(graph.dependencies),
            "vision": vision_text,
        }
        print("DEBUG BUILDING PMM MODULE FRAGMENT")
        prompt = build_prompt("module_pmm", payload)
        result = run_reasoning(prompt)

        fragment = result.get("text")
        print(f"DEBUG fragment module: {module_name}")

        print(f"DEBUG fragment: {fragment}")

        if isinstance(fragment, dict):
            fragments.append(fragment)

    return fragments


# =========================================================
# Reconciliation
# =========================================================

def _reconcile_fragments(
    fragments: List[dict],
    structural_graph: StructuralGraph,
    vision_text: str | None,
) -> dict:

    allowed_symbol_ids: Set[str] = {
        s.id for s in structural_graph.symbols
    }

    allowed_dependency_keys: Set[str] = {
        d.key for d in structural_graph.dependencies
    }

    payload = {
        "fragments": fragments,
        "allowed_symbol_ids": sorted(allowed_symbol_ids),
        "allowed_dependency_keys": sorted(allowed_dependency_keys),
        "vision": vision_text,
        "constraint": (
            "You may introduce new capabilities only if supported "
            "by allowed symbol IDs and dependency keys."
        ),
    }
    print("DEBUG: RECONCILING PMM FRAGMENTS")
    prompt = build_prompt("reconcile_pmm", payload)
    result = run_reasoning(prompt)

    text = result.get("text")
    return text if isinstance(text, dict) else {}


# =========================================================
# Validation (Strict Drop Policy)
# =========================================================
def _validate_capabilities(
    capabilities: List[dict],
    structural_graph: StructuralGraph,
) -> List[Capability]:

    symbol_ids = {s.id for s in structural_graph.symbols}
    dependency_keys = {d.key for d in structural_graph.dependencies}

    validated: List[Capability] = []

    for cap in capabilities:
        
        name = cap.get("name")
        description = cap.get("description")
        supported_symbols = cap.get("supported_symbol_ids", [])
        supported_deps = cap.get("supported_dependency_keys", [])

        # --------------------------
        # Structural validation
        # --------------------------

        if not isinstance(name, str) or not name.strip():
            continue

        if not isinstance(description, str) or not description.strip():
            continue

        if not supported_symbols or not supported_deps:
            continue

        if any(s not in symbol_ids for s in supported_symbols):
            continue

        if any(d not in dependency_keys for d in supported_deps):
            continue

        print("DEBUG RAW CAP:", cap)
        print("DEBUG supported_symbols:", supported_symbols)
        print("DEBUG supported_deps:", supported_deps)

        validated.append(
            Capability(
                name=name.strip(),
                description=description.strip(),
                supported_symbol_ids=sorted(supported_symbols),
                supported_dependency_keys=sorted(supported_deps),
                origin=cap.get("origin", "AI"),
            )
        )

    # Semantic-deterministic ordering
    return sorted(validated, key=lambda c: (c.name.lower(), c.description.lower()))

def _validate_guarantees(
    guarantees: List[dict],
    structural_graph: StructuralGraph,
) -> List[Guarantee]:

    symbol_ids = {s.id for s in structural_graph.symbols}
    dependency_keys = {d.key for d in structural_graph.dependencies}

    validated: List[Guarantee] = []

    for g in guarantees:

        statement = g.get("statement")
        enforced_symbols = g.get("enforced_symbol_ids", [])
        enforced_deps = g.get("enforced_dependency_keys", [])

        # --------------------------
        # Structural validation
        # --------------------------

        if not isinstance(statement, str) or not statement.strip():
            continue

        if not enforced_symbols or not enforced_deps:
            continue

        if any(s not in symbol_ids for s in enforced_symbols):
            continue

        if any(d not in dependency_keys for d in enforced_deps):
            continue

        validated.append(
            Guarantee(
                statement=statement.strip(),
                enforced_symbol_ids=sorted(enforced_symbols),
                enforced_dependency_keys=sorted(enforced_deps),
                origin=g.get("origin", "AI"),
            )
        )

    return sorted(validated, key=lambda g: g.statement.lower())