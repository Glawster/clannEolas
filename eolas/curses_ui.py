"""Keyboard-focused curses forms for private Eolas data entry."""

import curses
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Mapping, Sequence, Tuple

from eolas.capture.models import CAPTURE_PROFILES
from eolas.clann.models import ClannInput, PersonInput


class CursesCancelled(RuntimeError):
    """Raised when the user presses ``q`` to leave a form."""


@dataclass(frozen=True)
class FieldChoice:
    """A stored value and human-readable menu label."""

    value: str
    label: str


CLASSIFICATION_CHOICES = (
    FieldChoice("private", "Private"),
    FieldChoice("confidential", "Confidential"),
)
STATUS_CHOICES = (
    FieldChoice("active", "Active"),
    FieldChoice("inactive", "Inactive"),
    FieldChoice("closed", "Closed"),
    FieldChoice("unknown", "Unknown"),
)
ESSENTIALITY_CHOICES = (
    FieldChoice("essential", "Essential"),
    FieldChoice("important", "Important"),
    FieldChoice("nonEssential", "Non-essential"),
    FieldChoice("unknown", "Unknown"),
)

FIELD_CHOICES: Mapping[str, Sequence[FieldChoice]] = {
    "classification": CLASSIFICATION_CHOICES,
    "essentiality": ESSENTIALITY_CHOICES,
    "status": STATUS_CHOICES,
}

INSTRUCTION_PAIR = 1
MENU_PAIR = 2
ERROR_PAIR = 3
SUCCESS_PAIR = 4


class CursesForm:
    """Small reusable collection of curses data-entry controls."""

    def __init__(self, window: "curses.window") -> None:
        self.window = window
        self.window.keypad(True)
        self.instructionAttribute = curses.A_NORMAL
        self.menuAttribute = curses.A_NORMAL
        self.errorAttribute = curses.A_BOLD
        self.successAttribute = curses.A_BOLD
        self._coloursInitialize()

    def confirmationAsk(self, prompt: str, *, default: bool = False) -> bool:
        """Read an immediate yes/no response; q quits and s uses the default."""
        while True:
            self._pageDraw(prompt, "y yes | n no | s skip/default | q quit")
            key = self.window.getch()
            if key in (ord("y"), ord("Y")):
                return True
            if key in (ord("n"), ord("N")):
                return False
            if key in (ord("s"), ord("S")):
                return default
            if key in (ord("q"), ord("Q")):
                raise CursesCancelled("Data entry cancelled.")

    def menuAsk(
        self,
        prompt: str,
        choices: Sequence[FieldChoice],
        *,
        allowSkip: bool = True,
    ) -> str:
        """Choose an item with arrow keys and Enter."""
        selected = 0
        while True:
            hint = "Use arrows and Enter | q quit"
            if allowSkip:
                hint += " | s unknown"
            self._menuDraw(prompt, hint, choices, selected)
            key = self.window.getch()
            if key in (curses.KEY_UP, ord("k")):
                selected = (selected - 1) % len(choices)
            elif key in (curses.KEY_DOWN, ord("j")):
                selected = (selected + 1) % len(choices)
            elif key in (curses.KEY_ENTER, 10, 13):
                return choices[selected].value
            elif allowSkip and key in (ord("s"), ord("S")):
                return "unknown"
            elif key in (ord("q"), ord("Q")):
                raise CursesCancelled("Data entry cancelled.")

    def textAsk(self, prompt: str, *, allowSkip: bool = True) -> str:
        """Read editable text; q and s act immediately on an empty field."""
        while True:
            hint = "Enter text, then press Enter"
            if allowSkip:
                hint += " | s unknown"
            hint += " | q quit"
            value = ""
            while True:
                self._linesDraw([prompt, "", hint, "", f"> {value}"])
                key = self.window.get_wch()
                if not value and key in ("q", "Q"):
                    raise CursesCancelled("Data entry cancelled.")
                if not value and allowSkip and key in ("s", "S"):
                    return "unknown"
                if key in (curses.KEY_ENTER, "\n", "\r"):
                    cleaned = value.strip()
                    if cleaned:
                        return cleaned
                    self._messageShow("A value is required. Press any key.")
                    break
                if key in (curses.KEY_BACKSPACE, "\b", "\x7f"):
                    value = value[:-1]
                elif isinstance(key, str) and key.isprintable():
                    width = max(1, self.window.getmaxyx()[1] - 4)
                    if len(value) < width:
                        value += key

    def _linesDraw(self, lines: Sequence[str]) -> None:
        self.window.erase()
        height, width = self.window.getmaxyx()
        for row, line in enumerate(lines[: max(0, height - 1)]):
            self.window.addnstr(
                row,
                0,
                line,
                max(1, width - 1),
                self.instructionAttribute,
            )
        self.window.refresh()

    def _messageShow(self, message: str) -> None:
        self.window.erase()
        width = max(1, self.window.getmaxyx()[1] - 1)
        self.window.addnstr(0, 0, message, width, self.errorAttribute)
        self.window.refresh()
        self.window.getch()

    def _menuDraw(
        self,
        prompt: str,
        hint: str,
        choices: Sequence[FieldChoice],
        selected: int,
    ) -> None:
        self.window.erase()
        height, width = self.window.getmaxyx()
        usableWidth = max(1, width - 1)
        self.window.addnstr(0, 0, prompt, usableWidth, self.instructionAttribute)
        self.window.addnstr(2, 0, hint, usableWidth, self.instructionAttribute)
        for index, choice in enumerate(choices):
            row = index + 4
            if row >= height - 1:
                break
            label = f" {choice.label}".ljust(usableWidth)
            attribute = self.menuAttribute
            if index == selected:
                attribute |= curses.A_REVERSE
            self.window.addnstr(row, 0, label, usableWidth, attribute)
        self.window.refresh()

    def _coloursInitialize(self) -> None:
        try:
            if not curses.has_colors():
                return
            curses.start_color()
            if getattr(curses, "COLORS", 0) >= 256:
                blue, yellow, white, red, green = 17, 226, 15, 196, 34
            else:
                blue = curses.COLOR_BLUE
                yellow = curses.COLOR_YELLOW
                white = curses.COLOR_WHITE
                red = curses.COLOR_RED
                green = curses.COLOR_GREEN
            curses.init_pair(INSTRUCTION_PAIR, yellow, blue)
            curses.init_pair(MENU_PAIR, white, blue)
            curses.init_pair(ERROR_PAIR, white, red)
            curses.init_pair(SUCCESS_PAIR, white, green)
            self.instructionAttribute = curses.color_pair(INSTRUCTION_PAIR)
            self.menuAttribute = curses.color_pair(MENU_PAIR)
            self.errorAttribute = curses.color_pair(ERROR_PAIR) | curses.A_BOLD
            self.successAttribute = curses.color_pair(SUCCESS_PAIR) | curses.A_BOLD
            self.window.bkgd(" ", self.menuAttribute)
        except curses.error:
            self.instructionAttribute = curses.A_NORMAL
            self.menuAttribute = curses.A_NORMAL
            self.errorAttribute = curses.A_BOLD
            self.successAttribute = curses.A_BOLD

    def _pageDraw(self, heading: str, hint: str) -> None:
        self._linesDraw([heading, "", hint])


def clannCapture() -> ClannInput:
    """Capture a Clann and its people through a curses form."""
    return curses.wrapper(_clannCaptureRun)


def clannPathCapture(clannPaths: Sequence[Path]) -> Path:
    """Choose an existing Clann directory from a curses menu."""
    choices = tuple(
        FieldChoice(str(path), path.name.replace("-", " ").title())
        for path in clannPaths
    )
    selected = curses.wrapper(
        lambda window: CursesForm(window).menuAsk(
            "Choose a Clann", choices, allowSkip=False
        )
    )
    return Path(selected)


def captureDomainCapture() -> str:
    """Choose one of the supported continuity domains."""
    choices = tuple(
        FieldChoice(domain, _fieldLabel(domain)) for domain in CAPTURE_PROFILES
    )
    return curses.wrapper(
        lambda window: CursesForm(window).menuAsk(
            "What would you like to capture?", choices, allowSkip=False
        )
    )


def confirmationCapture(prompt: str, *, default: bool = False) -> bool:
    """Show a standalone one-key confirmation screen."""
    return curses.wrapper(
        lambda window: CursesForm(window).confirmationAsk(prompt, default=default)
    )


def domainCapture(domain: str) -> Tuple[str, str, Dict[str, str]]:
    """Capture a label and all mandatory fields for a domain profile."""
    return curses.wrapper(lambda window: _domainCaptureRun(window, domain))


def _clannCaptureRun(window: "curses.window") -> ClannInput:
    form = CursesForm(window)
    name = form.textAsk("Clann name", allowSkip=False)
    householdName = form.textAsk("Primary household name", allowSkip=False)
    people: List[PersonInput] = []
    while True:
        fullName = form.textAsk("Person's full name", allowSkip=False)
        preferredName = form.textAsk("Preferred name", allowSkip=False)
        householdRole = form.textAsk("Household role", allowSkip=False)
        isAdult = form.confirmationAsk("Is this person legally an adult?", default=True)
        isResident = form.confirmationAsk(
            "Does this person live in the primary household?", default=True
        )
        people.append(
            PersonInput(
                fullName,
                preferredName,
                householdRole,
                isAdult,
                lives_in_primary_household=isResident,
            )
        )
        if not form.confirmationAsk("Add another person?", default=False):
            break

    primaryChoices = tuple(
        FieldChoice(str(index), person.full_name) for index, person in enumerate(people)
    )
    primaryIndex = int(
        form.menuAsk("Choose the primary person", primaryChoices, allowSkip=False)
    )
    return ClannInput(
        name,
        householdName,
        [
            PersonInput(
                person.full_name,
                person.preferred_name,
                person.household_role,
                person.is_adult,
                index == primaryIndex,
                person.lives_in_primary_household,
            )
            for index, person in enumerate(people)
        ],
    )


def _domainCaptureRun(
    window: "curses.window", domain: str
) -> Tuple[str, str, Dict[str, str]]:
    form = CursesForm(window)
    label = form.textAsk("Record label", allowSkip=False)
    source = form.textAsk("Information source", allowSkip=False)
    fields: Dict[str, str] = {}
    for field in CAPTURE_PROFILES[domain].required_fields:
        prompt = _fieldLabel(field)
        choices = FIELD_CHOICES.get(field)
        if choices:
            fields[field] = form.menuAsk(prompt, choices)
        else:
            fields[field] = form.textAsk(prompt)
    return label, source, fields


def _fieldLabel(field: str) -> str:
    label = ""
    for character in field:
        if character.isupper():
            label += " "
        label += character.lower()
    return label.capitalize()
