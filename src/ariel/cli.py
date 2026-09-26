"""Command line interface: `ariel` and `ariel doctor` (the adapter for typer and rich)."""

import json

import typer
from rich.console import Console
from rich.markup import escape
from rich.table import Table

from ariel.doctor import run_checks

app = typer.Typer(help="Ariel, a voice-first computer use agent for Windows.", add_completion=False)


@app.callback(no_args_is_help=True)
def main() -> None:
    """Ariel. In Phase 0 the only command is `ariel doctor`."""


@app.command()
def doctor(
    quick: bool = typer.Option(False, "--quick", help="Skip the checks that load a model."),
    as_json: bool = typer.Option(False, "--json", help="Print machine-readable JSON."),
) -> None:
    """Check every component; each failure comes with a one-line fix."""
    results = run_checks(quick=quick)
    if as_json:
        typer.echo(json.dumps([result.model_dump() for result in results], indent=2))
    else:
        table = Table(title="ariel doctor")
        for column in ("", "Check", "Detail", "Fix"):
            table.add_column(column, overflow="fold")
        for result in results:
            status = "[green]OK[/green]" if result.ok else "[red]FAIL[/red]"
            table.add_row(status, escape(result.name), escape(result.detail), escape(result.hint))
        Console().print(table)
    raise typer.Exit(0 if all(result.ok for result in results) else 1)
