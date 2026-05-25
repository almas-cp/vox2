"""Textual TUI application for vox."""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import ClassVar

from rich.syntax import Syntax
from rich.text import Text
from textual import on, work
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical
from textual.message import Message
from textual.screen import ModalScreen
from textual.widgets import (
    Button,
    Footer,
    Header,
    Input,
    Label,
    ListItem,
    ListView,
    RichLog,
    Static,
    TextArea,
)

from vox import __version__
from vox.api import ApiError, fetch_command_async
from vox.clipboard import copy_to_clipboard
from vox.executor import execute_command
from vox.history import add_entry, get_all, search, toggle_favorite
from vox.security import check_command

CSS_PATH = Path(__file__).parent / "vox.tcss"


# ── Danger confirmation modal ──────────────────────────────────────────


class DangerModal(ModalScreen[bool]):
    """Modal shown when a dangerous command is about to be executed."""

    def __init__(self, command: str, reason: str) -> None:
        super().__init__()
        self._command = command
        self._reason = reason

    def compose(self) -> ComposeResult:
        with Container(id="danger-dialog"):
            yield Label("⚠  DANGEROUS COMMAND", id="danger-title")
            yield Label(self._reason, id="danger-reason")
            yield Static(self._command, id="danger-command")
            with Horizontal(id="danger-buttons"):
                yield Button("Cancel", variant="primary", id="danger-cancel")
                yield Button("Execute Anyway", variant="error", id="danger-confirm")

    @on(Button.Pressed, "#danger-cancel")
    def on_cancel(self) -> None:
        self.dismiss(False)

    @on(Button.Pressed, "#danger-confirm")
    def on_confirm(self) -> None:
        self.dismiss(True)


# ── History sidebar ────────────────────────────────────────────────────


class HistorySelected(Message):
    """Fired when user selects a history entry."""

    def __init__(self, command: str, query: str) -> None:
        super().__init__()
        self.command = command
        self.query = query


class HistorySidebar(Vertical):
    """Sidebar showing command history with search."""

    def compose(self) -> ComposeResult:
        yield Label("📜 History", id="sidebar-title")
        yield Input(placeholder="Search history…", id="history-search")
        yield ListView(id="history-list")

    def on_mount(self) -> None:
        self._refresh_list()

    def _refresh_list(self, term: str = "") -> None:
        lv = self.query_one("#history-list", ListView)
        lv.clear()
        entries = search(term) if term else get_all()
        for entry in entries[:50]:  # cap displayed items
            fav = "★ " if entry.get("favorite") else "  "
            label = Text.assemble(
                (fav, "bold yellow" if entry.get("favorite") else "dim"),
                (entry.get("query", "")[:30], ""),
            )
            lv.append(ListItem(Label(label)))
        # Store entries for selection lookup
        self._entries = entries[:50]

    @on(Input.Changed, "#history-search")
    def on_search_changed(self, event: Input.Changed) -> None:
        self._refresh_list(event.value)

    @on(ListView.Selected, "#history-list")
    def on_item_selected(self, event: ListView.Selected) -> None:
        idx = event.list_view.index
        if idx is not None and 0 <= idx < len(self._entries):
            entry = self._entries[idx]
            self.post_message(HistorySelected(
                command=entry.get("command", ""),
                query=entry.get("query", ""),
            ))


# ── Main application ──────────────────────────────────────────────────


class VoxApp(App[None]):
    """Vox TUI — natural language to shell commands."""

    CSS_PATH = CSS_PATH.name
    TITLE = f"vox v{__version__}"
    SUB_TITLE = "Natural Language Shell Assistant"

    BINDINGS: ClassVar[list[Binding]] = [
        Binding("enter", "execute", "Execute", show=True),
        Binding("e", "edit", "Edit", show=True),
        Binding("c", "copy", "Copy", show=True),
        Binding("h", "toggle_history", "History", show=True),
        Binding("q", "quit", "Quit", show=True),
        Binding("escape", "cancel_edit", "Cancel Edit", show=False),
    ]

    def __init__(
        self,
        query: str,
        command: str | None = None,
        explain: bool = False,
        dry_run: bool = False,
    ) -> None:
        super().__init__(css_path=CSS_PATH)
        self._query = query
        self._command = command or ""
        self._explain = explain
        self._dry_run = dry_run
        self._editing = False
        self._executing = False
        self._cancel_event = asyncio.Event()

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)

        # History sidebar (hidden by default)
        sidebar = HistorySidebar(id="history-sidebar")
        sidebar.add_class("hidden")
        yield sidebar

        with Vertical(id="main-panel", classes="full-width"):
            yield Label(id="query-display")
            yield Label("⏳ Fetching command…", id="loading")

            with Container(id="command-panel"):
                yield Label("GENERATED COMMAND", id="command-label")
                yield Static(id="command-text")

            yield TextArea(id="edit-area", language="bash", theme="monokai")

            with Container(id="output-panel"):
                yield Label("OUTPUT", id="output-label")
                yield RichLog(id="output-log", highlight=True, markup=True)

        yield Footer()

    def on_mount(self) -> None:
        self.query_one("#query-display", Label).update(f"❯ {self._query}")

        if self._command:
            self._show_command(self._command)
        else:
            self._fetch_api_command()

    @work(exclusive=True, thread=False)
    async def _fetch_api_command(self) -> None:
        loading = self.query_one("#loading", Label)
        loading.add_class("visible")
        cmd_panel = self.query_one("#command-panel", Container)

        try:
            result = await fetch_command_async(self._query)
            self._command = result
            self._show_command(result)
            add_entry(self._query, result)
        except ApiError as exc:
            self._command = ""
            cmd_text = self.query_one("#command-text", Static)
            cmd_text.update(Text(f"Error: {exc}", style="bold red"))
            cmd_panel.remove_class("danger")
        finally:
            loading.remove_class("visible")

    def _show_command(self, cmd: str) -> None:
        cmd_text = self.query_one("#command-text", Static)
        syntax = Syntax(cmd, "bash", theme="monokai", word_wrap=True)
        cmd_text.update(syntax)

        # Check for danger
        is_dangerous, reason = check_command(cmd)
        cmd_panel = self.query_one("#command-panel", Container)
        if is_dangerous:
            cmd_panel.add_class("danger")
        else:
            cmd_panel.remove_class("danger")

        loading = self.query_one("#loading", Label)
        loading.remove_class("visible")

        if self._dry_run:
            log = self.query_one("#output-log", RichLog)
            log.write("[bold yellow]--dry-run mode:[/] Command will not be executed.")

    # ── Actions ────────────────────────────────────────────────────

    def action_execute(self) -> None:
        if self._editing or self._executing or not self._command:
            return

        is_dangerous, reason = check_command(self._command)
        if is_dangerous:
            self.push_screen(DangerModal(self._command, reason), self._on_danger_result)
        else:
            self._run_command()

    def _on_danger_result(self, confirmed: bool) -> None:
        if confirmed:
            self._run_command()
        else:
            log = self.query_one("#output-log", RichLog)
            log.write("[bold red]Execution cancelled.[/]")

    @work(exclusive=True, thread=False)
    async def _run_command(self) -> None:
        if self._dry_run:
            log = self.query_one("#output-log", RichLog)
            log.write("[bold yellow]--dry-run:[/] Skipping execution.")
            return

        self._executing = True
        self._cancel_event.clear()
        log = self.query_one("#output-log", RichLog)
        log.clear()
        log.write(f"[bold cyan]$ {self._command}[/]\n")

        try:
            async for line in execute_command(self._command, cancel_event=self._cancel_event):
                log.write(line)
        except Exception as exc:
            log.write(f"\n[bold red]Error: {exc}[/]")
        finally:
            self._executing = False
            log.write("\n[dim]── done ──[/]")

    def action_edit(self) -> None:
        if self._executing or not self._command:
            return
        self._editing = True
        edit = self.query_one("#edit-area", TextArea)
        edit.load_text(self._command)
        edit.add_class("visible")
        edit.focus()

    def action_cancel_edit(self) -> None:
        if not self._editing:
            return
        self._editing = False
        edit = self.query_one("#edit-area", TextArea)
        # Apply edited command
        new_cmd = edit.text.strip()
        if new_cmd:
            self._command = new_cmd
            self._show_command(new_cmd)
        edit.remove_class("visible")

    def action_copy(self) -> None:
        if not self._command:
            return
        log = self.query_one("#output-log", RichLog)
        if copy_to_clipboard(self._command):
            log.write("[bold green]✔ Copied to clipboard[/]")
        else:
            log.write("[bold yellow]Clipboard unavailable — install xclip or xsel[/]")

    def action_toggle_history(self) -> None:
        sidebar = self.query_one("#history-sidebar", HistorySidebar)
        main = self.query_one("#main-panel", Vertical)
        if sidebar.has_class("hidden"):
            sidebar.remove_class("hidden")
            main.remove_class("full-width")
            sidebar._refresh_list()
        else:
            sidebar.add_class("hidden")
            main.add_class("full-width")

    @on(HistorySelected)
    def on_history_selected(self, event: HistorySelected) -> None:
        self._query = event.query
        self._command = event.command
        self.query_one("#query-display", Label).update(f"❯ {event.query}")
        self._show_command(event.command)
        log = self.query_one("#output-log", RichLog)
        log.clear()
        log.write("[dim]Loaded from history[/]")
