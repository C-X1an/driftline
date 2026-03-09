from __future__ import annotations

from pathlib import Path
from typing import List

from rich import print
import typer

from core.runtime.config import load_config, save_config


def choose_vision_path(candidates: List[Path]) -> Path:
    """
    Ask user to choose a vision.md when multiple exist.
    Persist the chosen path into config.json.
    """

    if not candidates:
        raise ValueError("No vision candidates provided")

    # -----------------------------------------------------
    # Display choices
    # -----------------------------------------------------
    print("\n[bold]Multiple vision.md files found:[/bold]\n")

    for i, path in enumerate(candidates, start=1):
        print(f"{i}) {path}")

    print()

    # -----------------------------------------------------
    # Prompt user
    # -----------------------------------------------------
    while True:
        try:
            choice = typer.prompt("Select the vision file number")
            index = int(choice) - 1

            if 0 <= index < len(candidates):
                selected = candidates[index]
                break

        except Exception:
            pass

        print("[red]Invalid selection. Please enter a valid number.[/red]")

    # -----------------------------------------------------
    # Persist to config
    # -----------------------------------------------------
    config = load_config()
    config.vision_path = str(selected)
    save_config(config)

    # -----------------------------------------------------
    # Inform user
    # -----------------------------------------------------
    print(
        "\n[green]Vision path saved to .driftline/config.json[/green]\n"
        "You can change it manually or via future Driftline CLI commands.\n"
    )

    return selected