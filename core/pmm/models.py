from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from typing import List


# -----------------------------------------
# Capability
# -----------------------------------------

@dataclass
class Capability:
    id: str
    name: str
    description: str
    source_files: List[str] = field(default_factory=list)
    related_symbols: List[str] = field(default_factory=list)


# -----------------------------------------
# Guarantee
# -----------------------------------------

@dataclass
class Guarantee:
    id: str
    statement: str
    strength: str  # weak | implied | enforced | critical
    evidence_symbols: List[str] = field(default_factory=list)
    source_files: List[str] = field(default_factory=list)


# -----------------------------------------
# Component
# -----------------------------------------

@dataclass
class Component:
    id: str
    name: str
    type: str  # module | class | function | service | route | etc.
    file_path: str


# -----------------------------------------
# Relationship
# -----------------------------------------

@dataclass
class Relationship:
    source_id: str
    target_id: str
    type: str  # implements | enforces | calls | depends_on


# -----------------------------------------
# Project Meaning Model (PMM)
# -----------------------------------------

@dataclass
class ProjectMeaningModel:
    repo_id: str
    generated_at: datetime

    capabilities: List[Capability] = field(default_factory=list)
    guarantees: List[Guarantee] = field(default_factory=list)
    components: List[Component] = field(default_factory=list)
    relationships: List[Relationship] = field(default_factory=list)

    # -------------------------------------
    # Convenience helpers
    # -------------------------------------

    def add_capability(self, capability: Capability) -> None:
        self.capabilities.append(capability)

    def add_guarantee(self, guarantee: Guarantee) -> None:
        self.guarantees.append(guarantee)

    def add_component(self, component: Component) -> None:
        self.components.append(component)

    def add_relationship(self, relationship: Relationship) -> None:
        self.relationships.append(relationship)