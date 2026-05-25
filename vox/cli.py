"""CLI entry point — Typer app that parses flags and launches the TUI."""

from __future__ import annotations

import sys
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.syntax import Syntax

from vox import __version__
from vox.api import ApiError, fetch_command
from vox.clipboard import copy_to_clipboard
from vox.executor import execute_command_sync
from vox.history import add_entry
from vox.security import check_command

console = Console()
app = typer.Typer(
    add_completion=False,
    no_args_is_help=True,
    rich_markup_mode="rich",
    help="[bold cyan]vox[/] — natural language to shell command assistant",
)


def version_callback(value: bool) -> None:
    if value:
        console.print(f"[bold cyan]vox[/] v{__version__}")
        raise typer.Exit()


@app.command(
    context_settings={"allow_extra_args": True, "ignore_unknown_options": True},
    help="Translate natural language into shell commands.",
)
def main(
    ctx: typer.Context,
    no_tui: bool = typer.Option(False, "--no-tui", help="Use inline Rich mode instead of TUI"),
    explain: bool = typer.Option(False, "--explain", help="Explain the generated command"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show command without executing"),
    voice: bool = typer.Option(False, "--voice", help="Voice input mode (coming soon)"),
    theme: str = typer.Option("dark", "--theme", help="Theme: dark or light"),
    version: Optional[bool] = typer.Option(
        None, "--version", "-v", callback=version_callback, is_eager=True,
        help="Show version",
    ),
) -> None:
    """Translate natural language into shell commands."""
    if voice:
        console.print("[bold yellow]🎙  Voice mode is not yet available.[/] Coming soon!")
        raise typer.Exit()

    # Join all extra args as the query
    query = " ".join(ctx.args).strip()
    if not query:
        console.print("[bold red]Please provide a query.[/] Example: [cyan]vox list all files[/]")
        raise typer.Exit(1)

    if no_tui:
        _inline_mode(query, explain=explain, dry_run=dry_run)
    else:
        _tui_mode(query, explain=explain, dry_run=dry_run, theme=theme)


def _inline_mode(query: str, explain: bool = False, dry_run: bool = False) -> None:
    """Rich-only inline mode for minimal terminals / SSH."""
    with console.status("[bold cyan]Thinking…[/]", spinner="dots"):
        try:
            command = fetch_command(query)
        except ApiError as exc:
            console.print(f"[bold red]Error:[/] {exc}")
            raise typer.Exit(1)

    # Display
    syntax = Syntax(command, "bash", theme="monokai", word_wrap=True)
    console.print()
    console.print(Panel(syntax, title="[bold]Generated Command[/]", border_style="cyan"))

    # Safety check
    is_dangerous, reason = check_command(command)
    if is_dangerous:
        console.print(f"\n[bold red]⚠  WARNING:[/] {reason}")

    if explain:
        console.print(
            Panel(
                f"[dim]Query:[/] {query}\n[dim]Command:[/] {command}",
                title="Explanation",
                border_style="yellow",
            )
        )

    add_entry(query, command)

    if dry_run:
        console.print("[bold yellow]--dry-run:[/] Not executing.")
        return

    # Prompt for action
    while True:
        choice = Prompt.ask(
            "\n[bold][E]xecute [e]dit [c]opy [q]uit[/]",
            choices=["E", "e", "c", "q"],
            default="E",
        )
        if choice == "q":
            return
        elif choice == "c":
            if copy_to_clipboard(command):
                console.print("[green]✔ Copied to clipboard[/]")
            else:
                console.print("[yellow]Clipboard unavailable[/]")
        elif choice == "e":
            edited = Prompt.ask("[bold]Edit command[/]", default=command)
            command = edited
            syntax = Syntax(command, "bash", theme="monokai", word_wrap=True)
            console.print(Panel(syntax, title="[bold]Edited Command[/]", border_style="green"))
            is_dangerous, reason = check_command(command)
            if is_dangerous:
                console.print(f"[bold red]⚠  WARNING:[/] {reason}")
        elif choice == "E":
            if is_dangerous:
                confirm = Prompt.ask(
                    "[bold red]This is a dangerous command. Execute anyway?[/]",
                    choices=["y", "n"],
                    default="n",
                )
                if confirm != "y":
                    continue
            console.print(f"\n[bold cyan]$ {command}[/]\n")
            execute_command_sync(command)
            return


def _tui_mode(
    query: str,
    explain: bool = False,
    dry_run: bool = False,
    theme: str = "dark",
) -> None:
    """Launch the full Textual TUI."""
    from vox.tui import VoxApp

    tui_app = VoxApp(query=query, explain=explain, dry_run=dry_run)
    if theme == "light":
        tui_app.dark = False
    tui_app.run()


def run() -> None:
    """Entry point for the `vox` console script."""
    app()


if __name__ == "__main__":
    run()
