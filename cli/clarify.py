from rich import print

from core.vision.loader import load_vision
from core.vision.models import VisionStatus
from core.vision.clarifier import (
    generate_clarification_questions,
    save_clarification_session,
    load_clarification_session,
    ClarificationSession,
)
from core.runtime.paths import get_driftline_dir


def clarify() -> None:
    """
    Generate clarification questions for the current vision.
    """

    vision_result = load_vision()

    if vision_result.status != VisionStatus.FOUND:
        print("[red]Vision not found.[/red]")
        print("Run: driftline init")
        return

    existing = load_clarification_session()
    if existing:
        print("[yellow]Clarification already exists.[/yellow]")
        print("[yellow]If you have answered the questions, run driftline finalize[/yellow]")
        return

    print("[cyan]Analyzing vision for ambiguities...[/cyan]")

    questions = generate_clarification_questions(vision_result)

    session = ClarificationSession(
        status="pending" if questions else "complete",
        questions=questions,
    )

    save_clarification_session(session)

    if not questions:
        print("[green]No clarification needed. Vision is precise.[/green]")
        return

    print("[green]Clarification questions generated.[/green]")
    print("Answer them in:")
    print(f"{get_driftline_dir() / 'clarification.json'}")
    print("\nAfter answering, run:")
    print("[bold]driftline finalize[/bold]")