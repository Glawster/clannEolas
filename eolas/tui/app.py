"""Textual terminal interface for Eolas.

The TUI is a presentation layer over Eolas application and domain services.
Business rules and persistence remain outside this package.
"""

from __future__ import annotations

from dataclasses import dataclass

from textual import on
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.events import Resize
from textual.screen import ModalScreen
from textual.widgets import (
    Button,
    DataTable,
    Footer,
    Header,
    Input,
    Label,
    ProgressBar,
    Static,
)


@dataclass(frozen=True)
class TuiPage:
    """Display content for one TUI page."""

    title: str
    subtitle: str
    columns: tuple[str, ...]
    rows: tuple[tuple[str, ...], ...]
    detail: str


PAGES = {
    "overview": TuiPage(
        "Family overview",
        "A calm summary of what is known, what is protected, and what needs attention.",
        ("Area", "Readiness", "Records", "Attention"),
        (
            ("People", "Ready", "5", "0"),
            ("Banking", "Good", "4", "1"),
            ("Insurance", "Review", "3", "1"),
            ("Subscriptions", "Good", "12", "2"),
            ("Documents", "Good", "18", "1"),
        ),
        "Next review: 14 November 2026\n"
        "3 items would benefit from attention. Nothing is urgent.",
    ),
    "people": TuiPage(
        "People & households",
        "Who belongs to the Clann, where they live, and the practical roles they hold.",
        ("Person", "Role", "Household", "Status"),
        (
            ("Alex Morgan", "Primary", "Oak House", "Ready"),
            ("Sam Morgan", "Partner", "Oak House", "Ready"),
            ("Jamie Morgan", "Family", "Oak House", "Review"),
            ("Pat Morgan", "Family", "Lives elsewhere", "Ready"),
        ),
        "Sensitive personal details are deliberately omitted from summary views.",
    ),
    "banking": TuiPage(
        "Banking",
        "Accounts are easy to find without exposing account numbers in the overview.",
        ("Institution", "Account", "Purpose", "Status"),
        (
            ("Example Bank", "•••• 4821", "Household current", "Ready"),
            ("Example Building Society", "•••• 1930", "Savings", "Ready"),
            ("Example Bank", "•••• 7714", "Bills", "Review"),
        ),
        "Select a record in a production UI to reveal permitted details, "
        "contacts, standing orders and continuity instructions.",
    ),
    "insurance": TuiPage(
        "Insurance",
        "Policies, renewal points and who to contact when something happens.",
        ("Policy", "Provider", "Renewal", "Status"),
        (
            ("Home", "Example Mutual", "Mar 2027", "Ready"),
            ("Car", "Example Cover", "Jan 2027", "Ready"),
            ("Life", "Example Life", "Review due", "Review"),
        ),
        "A future detail view can show claim instructions without exposing "
        "unnecessary personal data in the list.",
    ),
    "subscriptions": TuiPage(
        "Subscriptions & services",
        "Recurring commitments with clear cancellation and continuity information.",
        ("Service", "Category", "Paid by", "Status"),
        (
            ("Example Broadband", "Essential", "•••• 4821", "Ready"),
            ("Example Streaming", "Non-essential", "•••• 4821", "Ready"),
            ("Example Storage", "Important", "•••• 1930", "Review"),
        ),
        "The goal is practical continuity: what should continue, what can stop, "
        "and how a family member can act.",
    ),
    "documents": TuiPage(
        "Documents",
        "Important records presented by purpose rather than as an unstructured file list.",
        ("Document", "Held", "Review", "Status"),
        (
            ("Will", "Original + scan", "2027", "Ready"),
            ("Home insurance", "Digital", "Mar 2027", "Ready"),
            ("Property deeds", "Original", "Check location", "Review"),
        ),
        "Production views should show custody and access instructions before "
        "revealing protected document content.",
    ),
    "help": TuiPage(
        "Help & user guide",
        "What Eolas is for, how to begin, and what the main terms mean.",
        ("Topic", "Meaning", "What to do"),
        (
            (
                "Eolas",
                "A family continuity handbook",
                "Record practical knowledge others may need",
            ),
            (
                "Clann",
                "The wider group you are preparing for",
                "Include household and relevant family/support people",
            ),
            (
                "Readiness",
                "How complete and reviewable an area is",
                "Use it as a prompt, not a score",
            ),
            (
                "Review",
                "Information that may need checking",
                "Open the area and confirm it is still current",
            ),
            (
                "Capture",
                "Add structured continuity information",
                "Record the source and only necessary details",
            ),
        ),
        "Eolas is about continuity: helping trusted people understand what exists, "
        "where to find it and what practical action may be needed. It does not "
        "replace professional legal, medical or financial advice.\n\n"
        "Start small: complete one useful area, record where important originals "
        "are held, make sure an appropriate trusted person knows Eolas exists, "
        "and review information after significant changes and periodically.\n\n"
        "Do not store passwords, PINs, recovery codes, full payment-card security "
        "details or private cryptographic keys in Eolas. Summary screens should "
        "mask or omit sensitive values until an explicit detail view is appropriate.\n\n"
        "Navigation: use the numbered keys or arrow/tab navigation. Press q to quit.",
    ),
}


class ConfirmationModal(ModalScreen[None]):
    """Show safe confirmation before a data-changing action."""

    def __init__(self, label: str, source: str) -> None:
        super().__init__()
        self.label = label
        self.source = source

    def compose(self) -> ComposeResult:
        with Vertical(id="dialog"):
            yield Label("Save capture?", id="dialogTitle")
            yield Static(
                f"Label: {self.label}\nSource: {self.source}\n\n"
                "Review the details before continuing.",
                id="dialogBody",
            )
            with Horizontal(id="dialogButtons"):
                yield Button("Cancel", id="cancel")
                yield Button("Confirm preview", id="confirm", variant="primary")

    @on(Button.Pressed)
    def buttonPressed(self, event: Button.Pressed) -> None:
        """Close the prototype confirmation dialog."""

        self.dismiss()


class EolasApp(App[None]):
    """Full-screen terminal interface for Eolas."""

    CSS_PATH = "theme.tcss"
    TITLE = "Eolas"
    SUB_TITLE = "Family continuity"

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("1", "page('overview')", "Overview"),
        ("2", "page('people')", "People"),
        ("3", "page('banking')", "Banking"),
        ("4", "page('insurance')", "Insurance"),
        ("5", "page('subscriptions')", "Services"),
        ("6", "page('documents')", "Documents"),
        ("7", "page('capture')", "Capture"),
    ]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Horizontal(id="body"):
            with Vertical(id="navigation"):
                yield Label("EOLAS", id="brand")
                yield Static("Knowledge for continuity", id="tagline")
                yield Button("1  Overview", id="nav-overview", classes="navButton")
                yield Button("2  People", id="nav-people", classes="navButton")
                yield Button("3  Banking", id="nav-banking", classes="navButton")
                yield Button("4  Insurance", id="nav-insurance", classes="navButton")
                yield Button(
                    "5  Subscriptions", id="nav-subscriptions", classes="navButton"
                )
                yield Button("6  Documents", id="nav-documents", classes="navButton")
                yield Button("7  Quick capture", id="nav-capture", classes="navButton")
                yield Static(
                    "Keyboard first\nMouse optional",
                    id="navHint",
                )

            with VerticalScroll(id="workspace"):
                yield Label("Family overview", id="pageTitle")
                yield Static("", id="pageSubtitle")

                with Horizontal(id="summaryCards"):
                    yield Static("READINESS\n72%\nGood", classes="summaryCard")
                    yield Static("PEOPLE\n5\n2 households", classes="summaryCard")
                    yield Static("ATTENTION\n3\nNo urgent items", classes="summaryCard")

                yield Label("Overall readiness", id="readinessLabel")
                yield ProgressBar(total=100, show_eta=False, id="readiness")
                yield DataTable(id="records", zebra_stripes=True)
                yield Static("", id="detail")

                with Vertical(id="captureForm"):
                    yield Label("Quick capture", id="captureTitle")
                    yield Static(
                        "This demonstrates form entry and validation only. "
                        "A production TUI would call the same capture service as the CLI."
                    )
                    yield Label("Record label")
                    yield Input(
                        placeholder="e.g. Household emergency contact",
                        id="captureLabel",
                    )
                    yield Label("Information source")
                    yield Input(
                        placeholder="e.g. Policy document, conversation, statement",
                        id="captureSource",
                    )
                    yield Static("", id="validation")
                    yield Button(
                        "Preview save",
                        id="savePreview",
                        variant="primary",
                    )
        yield Footer()

    def on_mount(self) -> None:
        """Initialise the default dashboard state."""

        self.query_one("#readiness", ProgressBar).progress = 72
        self.layoutResponsive(self.size.width)
        self.pageShow("overview")

    def on_resize(self, event: Resize) -> None:
        """Apply responsive classes without relying on CSS media queries."""

        self.layoutResponsive(event.size.width)

    def layoutResponsive(self, width: int) -> None:
        """Set layout classes for compact and narrow terminal widths."""

        screen = self.screen
        screen.set_class(width < 80, "compact")
        screen.set_class(width < 60, "narrow")

    @on(Button.Pressed, ".navButton")
    def navigationPressed(self, event: Button.Pressed) -> None:
        """Switch page when a navigation button is pressed."""

        self.pageShow(event.button.id.removeprefix("nav-"))

    @on(Button.Pressed, "#savePreview")
    def savePreviewPressed(self) -> None:
        """Validate form fields before showing confirmation."""

        label = self.query_one("#captureLabel", Input).value.strip()
        source = self.query_one("#captureSource", Input).value.strip()
        validation = self.query_one("#validation", Static)

        missing = []
        if not label:
            missing.append("record label")
        if not source:
            missing.append("information source")
        if missing:
            validation.update("Required: " + ", ".join(missing))
            validation.add_class("error")
            return

        validation.update("Validated — ready for confirmation.")
        validation.remove_class("error")
        self.push_screen(ConfirmationModal(label, source))

    def action_page(self, pageName: str) -> None:
        """Open one of the numbered TUI pages."""

        self.pageShow(pageName)

    def pageShow(self, pageName: str) -> None:
        """Render one page while preserving the shared application shell."""

        capture = self.query_one("#captureForm", Vertical)
        cards = self.query_one("#summaryCards", Horizontal)
        progress = self.query_one("#readiness", ProgressBar)
        table = self.query_one("#records", DataTable)
        detail = self.query_one("#detail", Static)

        if pageName == "capture":
            self.query_one("#pageTitle", Label).update("Quick capture")
            self.query_one("#pageSubtitle", Static).update(
                "Structured entry without remembering a CLI command."
            )
            table.display = False
            cards.display = False
            progress.display = False
            detail.display = False
            capture.display = True
            self.query_one("#captureLabel", Input).focus()
            return

        page = PAGES[pageName]
        self.query_one("#pageTitle", Label).update(page.title)
        self.query_one("#pageSubtitle", Static).update(page.subtitle)
        capture.display = False
        table.display = True
        detail.display = True
        cards.display = pageName == "overview"
        progress.display = pageName == "overview"

        table.clear(columns=True)
        table.add_columns(*page.columns)
        table.add_rows(page.rows)
        table.cursor_type = "row"
        detail.update(page.detail)


def tuiRun() -> int:
    """Run the Eolas terminal interface."""

    EolasApp().run()
    return 0


def main() -> int:
    """Console entry point for the Eolas terminal interface."""

    return tuiRun()


if __name__ == "__main__":
    raise SystemExit(main())
