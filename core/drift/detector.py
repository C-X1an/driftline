from __future__ import annotations

from core.ai.runtime import run_reasoning
from core.ai.prompts.prompt_engine import build_prompt
from core.pmm.models import ProjectMeaningModel, serialize_capabilities, serialize_guarantees


# =========================================================
# Public API
# =========================================================

def detect_drift(
    vision_text: str,
    pmm: ProjectMeaningModel,
) -> dict:
    """
    Compare vision against PMM and detect semantic drift.

    Returns:
        {
            status,
            missing_vision_items,
            new_pmm_items,
            contradictions,
            summary,
            proposed_vision
        }
    """

    payload = {
        "vision": vision_text,
        "capabilities": serialize_capabilities(pmm),
        "guarantees": serialize_guarantees(pmm),
    }

    prompt = build_prompt("drift_compare", payload)

    result = run_reasoning(prompt)
    response = result.get("text")

    if not isinstance(response, dict):
        # If model fails JSON normalization,
        # treat as drift to avoid silent alignment.
        return {
            "status": "drifted",
            "missing_vision_items": [],
            "new_pmm_items": [],
            "contradictions": [],
            "summary": "AI response malformed.",
            "proposed_vision": vision_text,
        }

    return _validate_response(response, vision_text)


# =========================================================
# Validation Layer
# =========================================================

def _validate_response(response: dict, original_vision: str) -> dict:
    """
    Ensure required keys exist and enforce binary status.
    """

    required_keys = {
        "status",
        "missing_vision_items",
        "new_pmm_items",
        "contradictions",
        "summary",
        "proposed_vision",
    }

    if not required_keys.issubset(response.keys()):
        return {
            "status": "drifted",
            "missing_vision_items": [],
            "new_pmm_items": [],
            "contradictions": [],
            "summary": "Drift response missing required fields.",
            "proposed_vision": original_vision,
        }
    
    if not isinstance(response["missing_vision_items"], list):
        response["missing_vision_items"] = []

    if not isinstance(response["new_pmm_items"], list):
        response["new_pmm_items"] = []

    if not isinstance(response["contradictions"], list):
        response["contradictions"] = []

    if not isinstance(response["proposed_vision"], str):
        response["proposed_vision"] = original_vision

    # Enforce binary classification
    if response["status"] not in {"aligned", "drifted"}:
        response["status"] = "drifted"

    # If aligned, proposed vision must equal original
    if response["status"] == "aligned":
        response["proposed_vision"] = original_vision

    return response


