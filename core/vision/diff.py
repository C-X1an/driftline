from pathlib import Path
import subprocess
from rich import print
from core.runtime.paths import find_vscode_cli

def launch_diff(original: Path, proposed: Path) -> None:
    print("[yellow]Launching VSCode diff...[/yellow]")

    vscode_cli = find_vscode_cli()

    if vscode_cli is None:
        print("\n[bold red]VS Code CLI not found.[/bold red]\n")
        print("Driftline requires VS Code to visually compare vision changes.\n")
        print("Please ensure VS Code is installed and accessible.\n")
        print("Manually compare:")
        print(f"  Current:  {original}")
        print(f"  Proposed: {proposed}\n")
        return

    subprocess.run(
        [vscode_cli, "--diff", str(original), str(proposed)],
        check=False,
    )

    confirm = input("\nAfter reviewing/editing proposed file, apply changes? (y/N): ").strip().lower()

    if confirm == "y":
        final_content = proposed.read_text(encoding="utf-8")
        original.write_text(final_content, encoding="utf-8")
        print("[green]Vision updated successfully.[/green]")
    else:
        print("[yellow]No changes applied.[/yellow]")