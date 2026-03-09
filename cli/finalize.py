from rich import print
from pathlib import Path

from core.ai.runtime import run_reasoning
from core.ai.prompts.prompt_engine import build_prompt
from core.vision.loader import load_vision
from core.vision.models import VisionStatus
from core.vision.diff import launch_diff
from core.vision.clarifier import (
    load_clarification_session,
    save_clarification_session
)
from core.runtime.paths import get_driftline_dir


def finalize() -> None:
    """
    Apply clarification answers to vision.md.
    """

    vision_result = load_vision()

    if vision_result.status != VisionStatus.FOUND:
        print("[red]Vision not found.[/red]")
        return

    session = load_clarification_session()

    if not session:
        print("[red]No clarification session found.[/red]")
        print("Run: driftline clarify")
        return

    unanswered = [
        q for q in session.questions
        if not q.answer.strip()
    ]

    if unanswered:
        print("[red]Some clarification questions are unanswered.[/red]")
        print("Please complete all answers first.")
        return

    print("[cyan]Applying clarifications to vision...[/cyan]")

    payload = {
        "original_vision": vision_result.raw_text,
        "clarifications": [
            {
                "question": q.question,
                "answer": q.answer,
            }
            for q in session.questions
        ],
    }

    prompt = build_prompt("apply_clarifications", payload)
    result = run_reasoning(prompt)

    refined_payload = result.get("text")

    if not isinstance(refined_payload, dict):
        print("[red]Failed to generate refined vision.[/red]")
        return

    refined_text = refined_payload.get("rewritten_vision_markdown")

    if not isinstance(refined_text, str) or not refined_text.strip():
        print("[red]AI returned invalid vision content.[/red]")
        return

    if refined_text.strip() == vision_result.raw_text.strip():
        print("[green]No changes required after clarification.[/green]")
        return

    driftline_dir = get_driftline_dir()
    tmp_dir = driftline_dir / "tmp"
    tmp_dir.mkdir(parents=True, exist_ok=True)

    refined_path = tmp_dir / "vision_proposed.md"
    refined_path.write_text(refined_text, encoding="utf-8")

    launch_diff(vision_result.path, refined_path)

    session.status = "complete"
    save_clarification_session(session)

    print("\nIf you approve the changes, accept the edit request.")