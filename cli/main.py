import typer
from pathlib import Path
from rich import print

from cli.check import check
from cli.init import init
from cli.clarify import clarify
from cli.finalize import finalize
from cli.install_hook import install_hook


app = typer.Typer(help="Driftline — vision drift detection for real software.")


@app.callback()
def root():
    """
    Driftline CLI root.
    """
    pass

# ---------------------------------------------------------
# Commands
# ---------------------------------------------------------

app.command("init")(init)
app.command("check")(check)
app.command("clarify")(clarify)
app.command("finalize")(finalize)
app.command("install-hook")(install_hook)

# ---------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------

def main():
    app()


if __name__ == "__main__":
    main()