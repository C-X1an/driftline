from __future__ import annotations

from pathlib import Path
from rich import print

from core.runtime.paths import get_driftline_dir
from core.structure.scanner import scan_repository
from core.pmm.builder import build_pmm
from core.drift.detector import detect_drift
from core.vision.loader import load_vision
from core.vision.models import VisionStatus
from core.vision.clarifier import load_clarification_session
from core.vision.diff import launch_diff



# =========================================================
# CLI Command
# =========================================================

def check() -> None:
    """
    Run drift detection against current repository.
    """

    vision_result = load_vision()

    if vision_result.status != VisionStatus.FOUND:
        print("[red]Vision not found or invalid.[/red]")
        print("Run: driftline init")
        return

    vision_path = vision_result.path
    vision_text = vision_result.raw_text

    session = load_clarification_session()

    if vision_result.needs_clarification:
        if session is None:
            print("[yellow]Vision has not been clarified.[/yellow]")
            print("Run: driftline clarify")
        elif session.status == "pending":
            print("[yellow]Clarification answers are pending.[/yellow]")
            print("Complete answers and run: driftline finalize")

    print("[cyan]Scanning repository...[/cyan]")
    structural_graph = scan_repository()

    print("[cyan]Building PMM...[/cyan]")
    pmm = build_pmm(structural_graph, vision_text)

    print("[cyan]Detecting drift...[/cyan]")
    result = detect_drift(vision_text, pmm)

    _print_summary(result)

    if result["status"] == "aligned":
        print("[green]Vision aligned with PMM.[/green]")
        return

    if result["status"] == "drifted":
        _launch_diff(vision_path, result["proposed_vision"])



def _print_summary(result: dict) -> None:

    print("\n[bold]=== Drift Summary ===[/bold]")
    print(f"Status: {result['status']}")
    print(f"Summary: {result['summary']}")

    if result["missing_vision_items"]:
        print("\n[red]Missing Vision Items:[/red]")
        for item in result["missing_vision_items"]:
            print(f"- {item}")

    if result["new_pmm_items"]:
        print("\n[yellow]New PMM Items:[/yellow]")
        for item in result["new_pmm_items"]:
            print(f"- {item}")

    if result["contradictions"]:
        print("\n[red]Contradictions:[/red]")
        for item in result["contradictions"]:
            print(f"- {item}")

    print("\n=========================\n")


def _launch_diff(vision_path: Path, proposed_content: str) -> None:

    driftline_dir = get_driftline_dir()
    tmp_dir = driftline_dir / "tmp"
    tmp_dir.mkdir(parents=True, exist_ok=True)

    proposed_path = tmp_dir / "vision_proposed.md"

    # Always overwrite
    proposed_path.write_text(proposed_content, encoding="utf-8")

    launch_diff(vision_path, proposed_path)

