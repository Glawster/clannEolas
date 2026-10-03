"""Top-level Clann management view for the Eolas TUI."""

from __future__ import annotations

from typing import Callable, Sequence

from textual import on
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.message import Message
from textual.widgets import Button, DataTable, Label, Static

from eolas.clann.catalog import ClannSummary, clannsDiscover


class ClannView(Vertical):
    """Present Clann-level actions without putting them in global navigation."""

    class CreateRequested(Message):
        """Request the Create Clann workflow."""

    def __init__(
        self,
        *,
        discoverService: Callable[[], Sequence[ClannSummary]] = clannsDiscover,
        **kwargs: object,
    ) -> None:
        super().__init__(**kwargs)
        self._discoverService = discoverService

    def compose(self) -> ComposeResult:
        yield Label("Clann", id="clannTitle")
        yield Static(
            "Manage the family group whose continuity information is held in Eolas.",
            classes="formIntro",
        )
        with Horizontal(classes="formButtons"):
            yield Button("Create new Clann", id="clannCreate", variant="primary")
            yield Button("Select / switch Clann", id="clannSwitch", disabled=True)
        yield Static(
            "Select / switch will be enabled as the active-Clann workflow is migrated.",
            id="clannHint",
        )
        yield Label("Available Clanns", classes="formSectionTitle")
        yield DataTable(id="availableClanns", zebra_stripes=True)
        yield Static("", id="clannStatus")

    def on_mount(self) -> None:
        """Prepare and populate the local Clann list."""

        table = self.query_one("#availableClanns", DataTable)
        table.add_columns("Clann", "Location")
        table.cursor_type = "row"
        self.refreshClanns()

    def refreshClanns(self) -> None:
        """Reload safe Clann summaries from the shared discovery service."""

        table = self.query_one("#availableClanns", DataTable)
        table.clear()
        clanns = list(self._discoverService())
        for clann in clanns:
            table.add_row(clann.name, str(clann.path))
        self.query_one("#clannStatus", Static).update(
            f"{len(clanns)} Clann{'s' if len(clanns) != 1 else ''} available."
            if clanns
            else "No Clanns have been created yet."
        )

    @on(Button.Pressed, "#clannCreate")
    def createPressed(self) -> None:
        """Open the Create Clann sub-workflow."""

        self.post_message(self.CreateRequested())
