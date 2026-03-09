import typer
from pathlib import Path
import subprocess
from rich import print

from core.runtime.paths import ensure_runtime_dirs, find_repo_root, get_driftline_dir, find_vscode_cli
from core.ai.runtime import ensure_runtime_installed, run_reasoning
from core.structure.scanner import scan_repository
from core.pmm.builder import build_pmm
from core.ai.prompts.prompt_engine import build_prompt
from core.vision.merger import merge_vision_sections
from core.vision.diff import launch_diff
from core.runtime.config import (
    DriftlineConfig,
    load_config,
    save_config,
    get_config_path,
)


def get_vision_path() -> Path:
    """
    Default vision file location:
    <repo-root>/vision.md
    """
    repo_root = find_repo_root()
    return repo_root / "vision.md"


def create_default_vision_file(path: Path) -> None:
    """
    Writes starter vision.md with clear guidance.
    """
    content = """# Project Vision

## Core Capabilities

## Guarantees

---

_This file is used by Driftline to detect meaningful drift from intent._
"""
    path.write_text(content, encoding="utf-8")


def init():
    """
    Initialize Driftline in the current repository.
    """

    # Ensure runtime directory exists
    driftline_dir = ensure_runtime_dirs()

    # Create vision.md if missing
    vision_path = get_vision_path()
    if not vision_path.exists():
        create_default_vision_file(vision_path)
        created = True
    else:
        created = False

    if created:
        print(f"Created vision file: [cyan]{vision_path}[/cyan]")
    else:
        print(f"Vision file already exists: [cyan]{vision_path}[/cyan]")

    # Initialize config.json if missing
    config_path = get_config_path()

    if not config_path.exists():
        default_config = DriftlineConfig(
            vision_path=str(vision_path),
            ignore_paths=[
                ".git",
                ".driftline",
                "node_modules",
                "venv",
                ".venv",
                "__pycache__",
                "vision.md",
            ],
        )
        save_config(default_config)
        print(f"Created config file: [cyan]{config_path}[/cyan]")
    else:
        print(f"Config file already exists: [cyan]{config_path}[/cyan]")

    ensure_runtime_installed()

    # Output
    print("[bold green]Driftline initialized.[/bold green]")
    print(f"Runtime directory: [cyan]{driftline_dir}[/cyan]")

    print("[cyan]Scanning repository...[/cyan]")
    structural_graph = scan_repository()

    print("DEBUG SYMBOL COUNT:", len(structural_graph.symbols))
    print("DEBUG DEP COUNT:", len(structural_graph.dependencies))

    print("[cyan]Building PMM...[/cyan]")
    existing_vision_text = ""
    if vision_path.exists():
        existing_vision_text = vision_path.read_text(encoding="utf-8")

    print("[yellow]Analyzing repository. This may take up to a minute depending on project size...[/yellow]")

    pmm = build_pmm(structural_graph, existing_vision_text)

    print("DEBUG PMM CAPABILITIES:", pmm.capabilities)
    print("DEBUG PMM GUARANTEES:", pmm.guarantees)

    payload = {
        "existing_vision": existing_vision_text,
        "capabilities": [
            {
                "name": c.name,
                "description": c.description,
            }
            for c in pmm.capabilities
        ],
        "guarantees": [
            {
                "statement": g.statement,
            }
            for g in pmm.guarantees
        ],
    }

    prompt = build_prompt("populate_vision", payload)
    result = run_reasoning(prompt)

    generated_sections = result.get("text")

    print("DEBUG AI RAW OUTPUT:", result.get("text"))

    if not isinstance(generated_sections, dict):
        print("[red]AI output invalid. Vision not modified.[/red]")
        return

    new_vision = merge_vision_sections(existing_vision_text, generated_sections)

    if isinstance(new_vision, str):
        if new_vision.strip() == existing_vision_text.strip():
            print("[green]Vision already aligned with PMM.[/green]")
            return
        
        driftline_dir = get_driftline_dir()
        tmp_dir = driftline_dir / "tmp"
        tmp_dir.mkdir(parents=True, exist_ok=True)

        proposed_path = tmp_dir / "vision_proposed.md"
        proposed_path.write_text(new_vision, encoding="utf-8")

        launch_diff(vision_path, proposed_path)

        