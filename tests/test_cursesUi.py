"""Tests for keyboard-focused curses controls."""

import curses
from typing import List

import pytest

from eolas.capture.guidance import fieldGuidanceGet
from eolas.curses_ui import (
    ACCOUNT_CATEGORY_CHOICES,
    BANKING_STATUS_CHOICES,
    CursesCancelled,
    CursesForm,
    FieldChoice,
    _clannCaptureRun,
    _fieldChoicesGet,
)


class FakeWindow:
    """Minimal curses window used to drive controls with known keys."""

    def __init__(
        self,
        keys: List[int] | None = None,
        textKeys: List[str | int] | None = None,
    ) -> None:
        self.keys = list(keys or [])
        self.textKeys = list(textKeys or [])
        self.drawCalls: List[tuple[object, ...]] = []

    def addnstr(self, *args: object) -> None:
        self.drawCalls.append(args)

    def erase(self) -> None:
        return None

    def bkgd(self, *_args: object) -> None:
        return None

    def getch(self) -> int:
        return self.keys.pop(0)

    def getmaxyx(self) -> tuple[int, int]:
        return 24, 80

    def wideCharGet(self) -> str | int:
        return self.textKeys.pop(0)

    get_wch = wideCharGet  # curses window API name used by the UI

    def keypad(self, _enabled: bool) -> None:
        return None

    def refresh(self) -> None:
        return None


@pytest.mark.parametrize(("key", "expected"), [(ord("y"), True), (ord("n"), False)])
def testConfirmationAskUsesSingleKey(key: int, expected: bool) -> None:
    assert CursesForm(FakeWindow([key])).confirmationAsk("Continue?") is expected


def testConfirmationAskSupportsSkipAndQuit() -> None:
    assert CursesForm(FakeWindow([ord("s")])).confirmationAsk("Continue?", default=True)
    with pytest.raises(CursesCancelled):
        CursesForm(FakeWindow([ord("q")])).confirmationAsk("Continue?")


def testMenuAskUsesArrowsEnterAndSkip() -> None:
    choices = (FieldChoice("first", "First"), FieldChoice("second", "Second"))

    selected = CursesForm(FakeWindow([curses.KEY_DOWN, 10])).menuAsk("Choose", choices)

    assert selected == "second"
    assert CursesForm(FakeWindow([ord("s")])).menuAsk("Choose", choices) == "unknown"


def testMenuAskHighlightsSelectedFullRowInReverseVideo() -> None:
    window = FakeWindow([10])

    CursesForm(window).menuAsk("Choose", (FieldChoice("first", "First"),))

    selectedCall = next(
        call for call in window.drawCalls if len(call) == 5 and call[0] == 4
    )
    assert selectedCall[3] == 79
    assert int(selectedCall[4]) & curses.A_REVERSE
    assert str(selectedCall[2]).endswith(" " * 73)


def testColoursInitializeUsesRequestedTheme(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    pairs: list[tuple[int, int, int]] = []
    monkeypatch.setattr(curses, "has_colors", lambda: True)
    monkeypatch.setattr(curses, "start_color", lambda: None)
    monkeypatch.setattr(curses, "init_pair", lambda *pair: pairs.append(pair))
    monkeypatch.setattr(curses, "color_pair", lambda pair: pair * 100)

    form = CursesForm(FakeWindow())

    assert pairs == [
        (1, curses.COLOR_YELLOW, curses.COLOR_BLUE),
        (2, curses.COLOR_WHITE, curses.COLOR_BLUE),
        (3, curses.COLOR_WHITE, curses.COLOR_RED),
        (4, curses.COLOR_WHITE, curses.COLOR_GREEN),
    ]
    assert form.instructionAttribute == 100
    assert form.menuAttribute == 200
    assert form.errorAttribute == 300 | curses.A_BOLD
    assert form.successAttribute == 400 | curses.A_BOLD


def testColoursInitializePrefersStable256ColourPalette(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    pairs: list[tuple[int, int, int]] = []
    monkeypatch.setattr(curses, "has_colors", lambda: True)
    monkeypatch.setattr(curses, "start_color", lambda: None)
    monkeypatch.setattr(curses, "COLORS", 256, raising=False)
    monkeypatch.setattr(curses, "init_pair", lambda *pair: pairs.append(pair))
    monkeypatch.setattr(curses, "color_pair", lambda pair: pair * 100)

    CursesForm(FakeWindow())

    assert pairs == [
        (1, 226, 17),
        (2, 15, 17),
        (3, 15, 196),
        (4, 15, 34),
    ]


def testTextAskUsesEnterTextAndRecognisesImmediateControlKeys() -> None:
    textKeys: List[str | int] = [*"Household bills", "\n"]
    assert CursesForm(FakeWindow(textKeys=textKeys)).textAsk("Label") == (
        "Household bills"
    )
    assert CursesForm(FakeWindow(textKeys=["s"])).textAsk("Optional") == "unknown"
    with pytest.raises(CursesCancelled):
        CursesForm(FakeWindow(textKeys=["q"])).textAsk("Optional")


def testTextAskSupportsBackspace() -> None:
    keys: List[str | int] = [*"Billx", curses.KEY_BACKSPACE, "s", "\n"]
    assert CursesForm(FakeWindow(textKeys=keys)).textAsk("Label") == "Bills"


def testBankingCaptureGuidanceExplainsSafeInputAndControlledValues() -> None:
    owners = fieldGuidanceGet("banking", "owners")
    reviewed = fieldGuidanceGet("banking", "lastReviewed")

    assert owners is not None
    assert "separated by commas" in owners.purpose
    assert reviewed is not None
    assert "YYYY-MM-DD" in reviewed.purpose
    assert _fieldChoicesGet("banking", "accountCategory") == ACCOUNT_CATEGORY_CHOICES
    assert _fieldChoicesGet("banking", "status") == BANKING_STATUS_CHOICES


def testTextAskDrawsGuidedPromptLines() -> None:
    window = FakeWindow(textKeys=[*"Bills", "\n"])

    CursesForm(window).textAsk(("Purpose", "Why this matters", "Example: Bills"))

    drawn = [str(call[2]) for call in window.drawCalls if len(call) == 5]
    assert drawn[:3] == ["Purpose", "Why this matters", "Example: Bills"]


def testClannCaptureExplainsAcceptableBootstrapInput() -> None:
    window = FakeWindow(
        keys=[ord("y"), ord("y"), ord("n"), 10],
        textKeys=[
            *"Wilson Family",
            "\n",
            *"29A",
            "\n",
            *"Andy Wilson",
            "\n",
            *"Andy",
            "\n",
            *"Owner",
            "\n",
        ],
    )

    captured = _clannCaptureRun(window)

    assert captured.name == "Wilson Family"
    drawn = [str(call[2]) for call in window.drawCalls if len(call) == 5]
    assert "Example: Wilson Family" in drawn
    assert "Examples: owner, partner, family, carer, lodger" in drawn
