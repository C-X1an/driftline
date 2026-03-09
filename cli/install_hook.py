from pathlib import Path
from rich import print
import stat

from core.runtime.paths import find_repo_root


DRIFTLINE_MARKER = "# --- Driftline Hook ---"


def install_hook() -> None:
    """
    Install non-blocking pre-commit hook for Driftline. Appends safely if hook already exists.
    """

    repo_root = find_repo_root()
    git_dir = repo_root / ".git"

    if not git_dir.exists():
        print("[red]No .git directory found. Not a git repository.[/red]")
        return

    hooks_dir = git_dir / "hooks"
    hooks_dir.mkdir(exist_ok=True)

    hook_path = hooks_dir / "pre-commit"

    driftline_block = f"""
{DRIFTLINE_MARKER}
echo "Running Driftline check..."
driftline check || true
# --- End Driftline Hook ---
"""

    if not hook_path.exists():
        # Create new hook
        hook_script = f"""#!/bin/sh
{driftline_block}
exit 0
"""
        hook_path.write_text(hook_script, encoding="utf-8")
        hook_path.chmod(hook_path.stat().st_mode | stat.S_IEXEC)

        print("[green]Driftline pre-commit hook installed.[/green]")
        return

    # Hook exists → read content
    existing = hook_path.read_text(encoding="utf-8")

    if DRIFTLINE_MARKER in existing:
        print("[yellow]Driftline hook already installed in pre-commit.[/yellow]")
        return

    # Append Driftline block
    updated = existing.rstrip() + "\n" + driftline_block
    hook_path.write_text(updated, encoding="utf-8")
    hook_path.chmod(hook_path.stat().st_mode | stat.S_IEXEC)

    print("[green]Driftline appended to existing pre-commit hook.[/green]")