"""CLI entry point — Typer app with Rich-powered interactive prompts."""

from __future__ import annotations

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
from vox.history import add_entry, get_all, search
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
    explain: bool = typer.Option(False, "--explain", help="Explain the generated command"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show command without executing"),
    voice: bool = typer.Option(False, "--voice", help="Voice input mode (coming soon)"),
    history_flag: bool = typer.Option(False, "--history", "-H", help="Show command history"),
    version: Optional[bool] = typer.Option(
        None, "--version", "-v", callback=version_callback, is_eager=True,
        help="Show version",
    ),
) -> None:
    """Translate natural language into shell commands."""
    if voice:
        console.print("[bold yellow]🎙  Voice mode is not yet available.[/] Coming soon!")
        raise typer.Exit()

    if history_flag:
        _show_history()
        raise typer.Exit()

    # Join all extra args as the query
    query = " ".join(ctx.args).strip()
    if not query:
        console.print("[bold red]Please provide a query.[/] Example: [cyan]vox list all files[/]")
        raise typer.Exit(1)

    _run_query(query, explain=explain, dry_run=dry_run)


def _show_history() -> None:
    """Display command history."""
    entries = get_all()
    if not entries:
        console.print("[dim]No history yet.[/]")
        return

    console.print(Panel("[bold]Command History[/]", border_style="cyan"))
    for i, entry in enumerate(entries[:30]):
        fav = "★" if entry.get("favorite") else " "
        console.print(
            f"  [dim]{i + 1:>3}[/] [yellow]{fav}[/]  "
            f"[bold]{entry.get('query', '')}[/]  →  [green]{entry.get('command', '')}[/]"
        )


def _run_query(query: str, explain: bool = False, dry_run: bool = False) -> None:
    """Fetch command from API and present interactive prompt."""
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

    # Interactive action loop
    while True:
        choice = Prompt.ask(
            "\n[bold]\\[E]xecute \\[e]dit \\[c]opy \\[q]uit[/]",
            choices=["E", "e", "c", "q"],
            default="E",
        )
        if choice == "q":
            return
        elif choice == "c":
            if copy_to_clipboard(command):
                console.print("[green]✔ Copied to clipboard[/]")
            else:
                console.print("[yellow]Clipboard unavailable — install xclip or xsel[/]")
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


def run() -> None:
    """Entry point for the `vox` console script."""
    app()


if __name__ == "__main__":
    run()
