"""Textual Quick Capture workflow backed by shared capture services."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Optional

from textual import on
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label, Select, Static

from eolas.capture.models import CAPTURE_PROFILES, CaptureInput, CaptureValidationError
from eolas.capture.service import CaptureWriteError, capturePrepare, captureWrite


def fieldLabel(field: str) -> str:
    """Convert a camelCase field name into a readable label."""

    label = ""
    for character in field:
        if character.isupper():
            label += " "
        label += character.lower()
    return label.capitalize()


class CaptureConfirmScreen(ModalScreen[bool]):
    """Confirm one prepared capture before persistence."""

    def __init__(self, summary: str) -> None:
        super().__init__()
        self.summary = summary

    def compose(self) -> ComposeResult:
        with Vertical(id="captureConfirmDialog"):
            yield Label("Save this record?", id="dialogTitle")
            yield Static(self.summary, id="captureConfirmSummary")
            with Horizontal(id="dialogButtons"):
                yield Button("Back", id="captureBack")
                yield Button("Save record", id="captureConfirm", variant="primary")

    @on(Button.Pressed, "#captureBack")
    def backPressed(self) -> None:
        """Return to the form without writing."""

        self.dismiss(False)

    @on(Button.Pressed, "#captureConfirm")
    def confirmPressed(self) -> None:
        """Confirm persistence."""

        self.dismiss(True)


class QuickCaptureView(Vertical):
    """Collect and persist one continuity record for the active Clann."""

    def __init__(self, **kwargs: object) -> None:
        super().__init__(**kwargs)
        self._clannPath: Optional[Path] = None
        self._clannName: Optional[str] = None
        self._fieldInputs: Dict[str, Input] = {}
        self._pendingPath: Optional[Path] = None
        self._pendingDocument: Optional[dict] = None

    def compose(self) -> ComposeResult:
        yield Label("Quick capture", id="captureTitle")
        yield Static("", id="captureClann")
        yield Static(
            "Choose a domain, load its required fields, then review before saving.",
            classes="formIntro",
        )
        yield Label("Domain")
        yield Select(
            [(fieldLabel(domain), domain) for domain in CAPTURE_PROFILES],
            prompt="Choose a domain",
            id="captureDomain",
        )
        yield Button("Load required fields", id="captureFieldsLoad")
        yield Label("Record label")
        yield Input(
            placeholder="A safe human-readable label",
            id="captureLabel",
        )
        yield Label("Information source")
        yield Input(
            placeholder="Where this information came from",
            id="captureSource",
        )
        yield VerticalScroll(id="captureFields")
        yield Static("", id="captureValidation")
        yield Button("Review & save", id="captureReview", variant="primary")

    def activeClannSet(self, name: str, path: Path) -> None:
        """Set the Clann that will own future captured records."""

        self._clannName = name
        self._clannPath = path
        self.query_one("#captureClann", Static).update(f"Active Clann: {name}")

    @on(Button.Pressed, "#captureFieldsLoad")
    async def fieldsLoadPressed(self) -> None:
        """Build fields from the selected shared capture profile."""

        selected = self.query_one("#captureDomain", Select).value
        if not isinstance(selected, str) or selected not in CAPTURE_PROFILES:
            self._statusShow("Choose a domain first.", error=True)
            return

        container = self.query_one("#captureFields", VerticalScroll)
        await container.remove_children()
        self._fieldInputs.clear()
        for field in CAPTURE_PROFILES[selected].required_fields:
            inputWidget = Input(
                placeholder=self._placeholderGet(field),
                id=f"captureField-{field}",
            )
            self._fieldInputs[field] = inputWidget
            await container.mount(Label(fieldLabel(field)), inputWidget)
        self._statusShow(
            f"Loaded {len(self._fieldInputs)} required fields for {fieldLabel(selected)}.",
            error=False,
        )

    @on(Button.Pressed, "#captureReview")
    def reviewPressed(self) -> None:
        """Validate through CaptureInput and prepare the shared persistence document."""

        if self._clannPath is None:
            self._statusShow(
                "Select an active Clann from the Clann screen before capturing data.",
                error=True,
            )
            return

        domainValue = self.query_one("#captureDomain", Select).value
        if not isinstance(domainValue, str) or domainValue not in CAPTURE_PROFILES:
            self._statusShow("Choose a domain first.", error=True)
            return

        expected = CAPTURE_PROFILES[domainValue].required_fields
        if tuple(self._fieldInputs) != expected:
            self._statusShow(
                "Load the required fields for the selected domain before saving.",
                error=True,
            )
            return

        fields = {
            field: inputWidget.value.strip()
            for field, inputWidget in self._fieldInputs.items()
        }
        capture = CaptureInput(
            domain=domainValue,
            label=self.query_one("#captureLabel", Input).value.strip(),
            fields=fields,
            source=self.query_one("#captureSource", Input).value.strip(),
        )
        try:
            targetPath, document = capturePrepare(capture, self._clannPath)
        except (CaptureValidationError, CaptureWriteError, OSError, ValueError) as error:
            self._statusShow(str(error), error=True)
            return

        self._pendingPath = targetPath
        self._pendingDocument = document
        summary = (
            f"Clann: {self._clannName}\n"
            f"Domain: {fieldLabel(domainValue)}\n"
            f"Label: {capture.label}\n"
            f"Source: {capture.source}\n"
            f"Target: {targetPath}"
        )
        self.app.push_screen(CaptureConfirmScreen(summary), self._saveConfirmed)

    def _saveConfirmed(self, confirmed: Optional[bool]) -> None:
        """Persist the already prepared document after explicit confirmation."""

        if not confirmed or self._pendingPath is None or self._pendingDocument is None:
            return
        try:
            captureWrite(self._pendingPath, self._pendingDocument)
        except (CaptureWriteError, OSError) as error:
            self._statusShow(f"Error: {error}", error=True)
            return

        savedPath = self._pendingPath
        self._pendingPath = None
        self._pendingDocument = None
        self.query_one("#captureLabel", Input).value = ""
        self.query_one("#captureSource", Input).value = ""
        for inputWidget in self._fieldInputs.values():
            inputWidget.value = ""
        self._statusShow(f"Saved: {savedPath}", error=False)

    def _statusShow(self, message: str, *, error: bool) -> None:
        status = self.query_one("#captureValidation", Static)
        status.update(message)
        status.set_class(error, "error")

    @staticmethod
    def _placeholderGet(field: str) -> str:
        if field == "classification":
            return "private or confidential"
        if field == "lastReviewed":
            return "YYYY-MM-DD"
        if field == "status":
            return "active, inactive, closed or unknown"
        if field == "essentiality":
            return "essential, important, nonEssential or unknown"
        return fieldLabel(field)
