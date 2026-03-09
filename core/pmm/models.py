from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List


@dataclass
class Capability:
    name: str
    description: str
    supported_symbol_ids: List[str]
    supported_dependency_keys: List[str]

    origin: str  # structural | AI



@dataclass
class Guarantee:
    statement: str
    enforced_symbol_ids: List[str]
    enforced_dependency_keys: List[str]

    origin: str  # structural | AI


# -----------------------------------------
# Project Meaning Model (PMM)
# -----------------------------------------

@dataclass
class ProjectMeaningModel:
    repo_id: str
    generated_at: datetime

    capabilities: List[Capability] = field(default_factory=list)
    guarantees: List[Guarantee] = field(default_factory=list)

    def add_capability(self, capability: Capability) -> None:
        self.capabilities.append(capability)

    def add_guarantee(self, guarantee: Guarantee) -> None:
        self.guarantees.append(guarantee)


def serialize_capabilities(pmm: ProjectMeaningModel) -> List[Dict]:
    return [
        {
            "name": cap.name,
            "description": cap.description,
        }
        for cap in pmm.capabilities
    ]


def serialize_guarantees(pmm: ProjectMeaningModel) -> List[Dict]:
    return [
        {
            "statement": g.statement,
        }
        for g in pmm.guarantees
    ]