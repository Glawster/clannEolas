"""Textual Create Clann workflow backed by the shared Clann service."""

from __future__ import annotations

from pathlib import Path
from typing import Callable, Optional

from textual import on
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Checkbox, DataTable, Input, Label, Static

from eolas.clann.models import ClannInput, ClannValidationError, PersonInput
from eolas.clann.service import ClannCreationError, clannCreate
from eolas.paths import dataRootGet


class ClannCreateConfirmScreen(ModalScreen[bool]):
    """Confirm the complete Clann summary before persistence."""

    def __init__(self, summary: str) -> None:
        super().__init__()
        self.summary = summary

    def compose(self) -> ComposeResult:
        with Vertical(id="clannConfirmDialog"):
            yield Label("Create this Clann?", id="dialogTitle")
            yield Static(self.summary, id="clannConfirmSummary")
            yield Static(
                "This creates private Eolas files on this computer.",
                id="dialogBody",
            )
            with Horizontal(id="dialogButtons"):
                yield Button("Back", id="clannCreateBack")
                yield Button(
                    "Create Clann",
                    id="clannCreateConfirm",
                    variant="primary",
                )

    @on(Button.Pressed, "#clannCreateBack")
    def backPressed(self) -> None:
        """Return to the form without writing data."""

        self.dismiss(False)

    @on(Button.Pressed, "#clannCreateConfirm")
    def confirmPressed(self) -> None:
        """Confirm creation."""

        self.dismiss(True)


class ClannCreateView(Vertical):
    """Create a Clann through a structured Textual workflow."""

    def __init__(
        self,
        *,
        dataRootProvider: Callable[[], Path] = dataRootGet,
        createService: Callable[[ClannInput, Path], Path] = clannCreate,
        **kwargs: object,
    ) -> None:
        super().__init__(**kwargs)
        self._people: list[PersonInput] = []
        self._pendingClann: Optional[ClannInput] = None
        self._dataRootProvider = dataRootProvider
        self._createService = createService

    def compose(self) -> ComposeResult:
        yield Label("Create a Clann", id="clannCreateTitle")
        yield Static(
            "A Clann is the group of people whose practical continuity "
            "information Eolas will help organise.",
            classes="formIntro",
        )

        yield Label("Clann name")
        yield Input(
            placeholder="e.g. Morgan Clann",
            id="clannName",
        )

        yield Label("Primary household name")
        yield Input(
            placeholder="e.g. Family Home",
            id="householdName",
        )

        yield Label("Add a person", classes="formSectionTitle")
        with Horizontal(classes="twoColumnFields"):
            with Vertical():
                yield Label("Full name")
                yield Input(placeholder="Full name", id="personFullName")
            with Vertical():
                yield Label("Preferred name")
                yield Input(placeholder="Preferred name", id="personPreferredName")

        yield Label("Household role")
        yield Input(
            placeholder="e.g. householder, partner, family, carer",
            id="personRole",
        )

        with Horizontal(id="personOptions"):
            yield Checkbox("Legally an adult", value=True, id="personAdult")
            yield Checkbox(
                "Lives in primary household",
                value=True,
                id="personResident",
            )

        with Horizontal(classes="formButtons"):
            yield Button("Add person", id="personAdd", variant="primary")
            yield Button("Remove selected", id="personRemove")

        yield Static("", id="personValidation")
        yield DataTable(id="clannPeople", zebra_stripes=True)

        with Horizontal(classes="formButtons"):
            yield Button("Set selected as primary", id="personSetPrimary")
            yield Button("Review & create", id="clannReview", variant="primary")

        yield Static("", id="clannValidation")

    def on_mount(self) -> None:
        """Prepare the people table."""

        table = self.query_one("#clannPeople", DataTable)
        table.add_columns("Primary", "Name", "Preferred", "Role", "Adult", "Resident")
        table.cursor_type = "row"

    @on(Button.Pressed, "#personAdd")
    def personAddPressed(self) -> None:
        """Validate and stage one person."""

        fullName = self.query_one("#personFullName", Input).value.strip()
        preferredName = self.query_one("#personPreferredName", Input).value.strip()
        householdRole = self.query_one("#personRole", Input).value.strip()
        isAdult = self.query_one("#personAdult", Checkbox).value
        isResident = self.query_one("#personResident", Checkbox).value

        person = PersonInput(
            full_name=fullName,
            preferred_name=preferredName,
            household_role=householdRole,
            is_adult=isAdult,
            is_primary=not self._people,
            lives_in_primary_household=isResident,
        )

        try:
            person.personValidate()
        except ClannValidationError as error:
            self._messageShow("#personValidation", str(error), error=True)
            return

        self._people.append(person)
        self._peopleTableRefresh()
        self._messageShow(
            "#personValidation",
            f"Added {person.full_name}.",
            error=False,
        )
        self.query_one("#personFullName", Input).value = ""
        self.query_one("#personPreferredName", Input).value = ""
        self.query_one("#personRole", Input).value = ""
        self.query_one("#personFullName", Input).focus()

    @on(Button.Pressed, "#personRemove")
    def personRemovePressed(self) -> None:
        """Remove the currently selected staged person."""

        index = self._selectedIndexGet()
        if index is None:
            self._messageShow(
                "#personValidation",
                "Select a person to remove.",
                error=True,
            )
            return

        removedWasPrimary = self._people[index].is_primary
        removed = self._people.pop(index)
        if removedWasPrimary and self._people:
            self._people[0] = self._personPrimarySet(self._people[0], True)
        self._peopleTableRefresh()
        self._messageShow(
            "#personValidation",
            f"Removed {removed.full_name}.",
            error=False,
        )

    @on(Button.Pressed, "#personSetPrimary")
    def personSetPrimaryPressed(self) -> None:
        """Set the selected staged person as the single primary person."""

        index = self._selectedIndexGet()
        if index is None:
            self._messageShow(
                "#personValidation",
                "Select a person first.",
                error=True,
            )
            return

        self._people = [
            self._personPrimarySet(person, personIndex == index)
            for personIndex, person in enumerate(self._people)
        ]
        self._peopleTableRefresh()
        self._messageShow(
            "#personValidation",
            f"{self._people[index].full_name} is the primary person.",
            error=False,
        )

    @on(Button.Pressed, "#clannReview")
    def clannReviewPressed(self) -> None:
        """Validate the complete form and show a safe review step."""

        clann = ClannInput(
            name=self.query_one("#clannName", Input).value.strip(),
            primary_household_name=self.query_one(
                "#householdName", Input
            ).value.strip(),
            people=list(self._people),
        )
        try:
            clann.clannValidate()
        except ClannValidationError as error:
            self._messageShow("#clannValidation", str(error), error=True)
            return

        self._pendingClann = clann
        self._messageShow("#clannValidation", "", error=False)
        self.app.push_screen(
            ClannCreateConfirmScreen(self._summaryBuild(clann)),
            self._creationConfirmed,
        )

    def reset(self) -> None:
        """Clear the workflow after successful creation."""

        self._people.clear()
        self._pendingClann = None
        for selector in (
            "#clannName",
            "#householdName",
            "#personFullName",
            "#personPreferredName",
            "#personRole",
        ):
            self.query_one(selector, Input).value = ""
        self.query_one("#personAdult", Checkbox).value = True
        self.query_one("#personResident", Checkbox).value = True
        self._peopleTableRefresh()
        self._messageShow("#personValidation", "", error=False)

    def _creationConfirmed(self, confirmed: Optional[bool]) -> None:
        """Persist the validated Clann only after explicit confirmation."""

        if not confirmed or self._pendingClann is None:
            return

        try:
            createdPath = self._createService(
                self._pendingClann,
                self._dataRootProvider(),
            )
        except (ClannCreationError, ClannValidationError, OSError, ValueError) as error:
            self._messageShow("#clannValidation", f"Error: {error}", error=True)
            return

        createdName = self._pendingClann.name
        self.reset()
        self._messageShow(
            "#clannValidation",
            f"Clann created: {createdName}\n{createdPath}",
            error=False,
        )

    def _peopleTableRefresh(self) -> None:
        table = self.query_one("#clannPeople", DataTable)
        table.clear()
        for person in self._people:
            table.add_row(
                "Yes" if person.is_primary else "",
                person.full_name,
                person.preferred_name,
                person.household_role,
                "Yes" if person.is_adult else "No",
                "Yes" if person.lives_in_primary_household else "No",
            )

    def _selectedIndexGet(self) -> Optional[int]:
        if not self._people:
            return None
        table = self.query_one("#clannPeople", DataTable)
        row = table.cursor_coordinate.row
        if 0 <= row < len(self._people):
            return row
        return None

    @staticmethod
    def _personPrimarySet(person: PersonInput, isPrimary: bool) -> PersonInput:
        return PersonInput(
            full_name=person.full_name,
            preferred_name=person.preferred_name,
            household_role=person.household_role,
            is_adult=person.is_adult,
            is_primary=isPrimary,
            lives_in_primary_household=person.lives_in_primary_household,
        )

    @staticmethod
    def _summaryBuild(clann: ClannInput) -> str:
        lines = [
            f"Clann: {clann.name}",
            f"Primary household: {clann.primary_household_name}",
            "",
            "People:",
        ]
        for person in clann.people:
            markers = []
            if person.is_primary:
                markers.append("primary")
            markers.append(
                "resident" if person.lives_in_primary_household else "lives elsewhere"
            )
            markers.append("adult" if person.is_adult else "minor")
            lines.append(
                f"  {person.full_name} — {person.household_role} "
                f"({', '.join(markers)})"
            )
        return "\n".join(lines)

    def _messageShow(self, selector: str, message: str, *, error: bool) -> None:
        target = self.query_one(selector, Static)
        target.update(message)
        target.set_class(error, "error")
