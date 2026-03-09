from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List, Optional

from core.runtime.paths import get_driftline_dir
from core.vision.models import VisionLoadResult
from core.ai.runtime import run_reasoning
from core.ai.prompts.prompt_engine import build_prompt


# ---------------------------------------------------------
# Data models
# ---------------------------------------------------------

@dataclass
class ClarificationQuestion:
    question: str
    answer: Optional[str] = None


@dataclass
class ClarificationSession:
    status: str  # "pending" | "complete"
    questions: List[ClarificationQuestion]


# ---------------------------------------------------------
# Paths
# ---------------------------------------------------------

CLARIFICATION_FILENAME = "clarification.json"


def get_clarification_path() -> Path:
    return get_driftline_dir() / CLARIFICATION_FILENAME


# ---------------------------------------------------------
# Session persistence
# ---------------------------------------------------------

def load_clarification_session() -> Optional[ClarificationSession]:
    path = get_clarification_path()

    if not path.exists():
        return None

    data = json.loads(path.read_text(encoding="utf-8"))

    questions = [
        ClarificationQuestion(**q)
        for q in data.get("questions", [])
    ]

    return ClarificationSession(
        status=data.get("status", "pending"),
        questions=questions,
    )


def save_clarification_session(session: ClarificationSession) -> None:
    path = get_clarification_path()

    data = {
        "status": session.status,
        "questions": [asdict(q) for q in session.questions],
    }

    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def generate_clarification_questions(vision: VisionLoadResult) -> List[ClarificationQuestion]:

    if vision.raw_text is None:
        return []

    payload = {
        "vision": vision.raw_text,
    }

    prompt = build_prompt("clarify_vision", payload)
    result = run_reasoning(prompt)

    response = result.get("text")

    if not isinstance(response, dict):
        return []

    questions = response.get("questions", [])

    if not isinstance(questions, list):
        return []

    return [
        ClarificationQuestion(
            question=q.get("question", "").strip(),
            answer=q.get("answer", "") or "",
        )
        for q in questions
        if isinstance(q, dict) and q.get("question")
    ]


# ---------------------------------------------------------
# Public API
# ---------------------------------------------------------
def ensure_clarification_session(vision: VisionLoadResult) -> ClarificationSession:

    existing = load_clarification_session()
    if existing:
        return existing

    questions = generate_clarification_questions(vision)

    session = ClarificationSession(
        status="pending" if questions else "complete",
        questions=questions,
    )

    save_clarification_session(session)
    return session