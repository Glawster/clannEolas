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

    class SelectRequested(Message):
        """Request that one discovered Clann become active."""

        def __init__(self, clann: ClannSummary) -> None:
            super().__init__()
            self.clann = clann

    def __init__(
        self,
        *,
        discoverService: Callable[[], Sequence[ClannSummary]] = clannsDiscover,
        **kwargs: object,
    ) -> None:
        super().__init__(**kwargs)
        self._discoverService = discoverService
        self._clanns: list[ClannSummary] = []
        self._activePath = None

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
            "Choose a row below, then select it as the active Clann.",
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
        self._clanns = list(self._discoverService())
        for clann in self._clanns:
            table.add_row(clann.name, str(clann.path))
        self.query_one("#clannStatus", Static).update(
            f"{len(self._clanns)} Clann{'s' if len(self._clanns) != 1 else ''} available."
            if self._clanns
            else "No Clanns have been created yet."
        )
        self.query_one("#clannSwitch", Button).disabled = not self._clanns

    @on(Button.Pressed, "#clannCreate")
    def createPressed(self) -> None:
        """Open the Create Clann sub-workflow."""

        self.post_message(self.CreateRequested())


    @on(Button.Pressed, "#clannSwitch")
    def switchPressed(self) -> None:
        """Make the selected discovered Clann the active session Clann."""

        if not self._clanns:
            return
        table = self.query_one("#availableClanns", DataTable)
        row = table.cursor_coordinate.row
        if not 0 <= row < len(self._clanns):
            self.query_one("#clannStatus", Static).update(
                "Select a Clann row first."
            )
            return
        self.post_message(self.SelectRequested(self._clanns[row]))

    def activeShow(self, clann: ClannSummary) -> None:
        """Show which Clann is active in the current application session."""

        self._activePath = clann.path
        self.query_one("#clannStatus", Static).update(
            f"Active Clann: {clann.name}"
        )
