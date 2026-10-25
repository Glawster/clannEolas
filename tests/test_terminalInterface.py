"""Interaction tests for the Textual Eolas terminal interface."""

import asyncio
from pathlib import Path

from textual.widgets import Button, DataTable, Input, Select, Static

from eolas.tui.app import EolasApp
from eolas.tui.views.clannCreate import ClannCreateConfirmScreen, ClannCreateView
from eolas.tui.views.quickCapture import CaptureConfirmScreen


async def _buttonActivate(app: EolasApp, pilot, selector: str) -> None:
    """Focus and activate a button, scrolling it into view first."""

    button = app.query_one(selector, Button)
    button.focus()
    await pilot.pause()
    await pilot.press("enter")
    await pilot.pause()


async def _modalButtonActivate(app: EolasApp, pilot, screenType, selector: str) -> None:
    """Wait for a pushed modal screen, then activate one of its buttons."""

    for _attempt in range(10):
        await pilot.pause()
        if isinstance(app.screen, screenType):
            button = app.screen.query_one(selector, Button)
            button.focus()
            await pilot.press("enter")
            await pilot.pause()
            return
    raise AssertionError(f"Expected modal screen {screenType.__name__} was not shown.")


def testTuiLoadsProjectStylesheetFromApplicationPath() -> None:
    """The TUI stylesheet is independent of the process working directory."""

    stylesheetPath = Path(EolasApp.CSS_PATH)

    assert stylesheetPath.name == "projectStyles.css"
    assert stylesheetPath.parent.name == "styles"
    assert stylesheetPath.is_file()


def testTuiStylesSelectWithSingleProjectBorder() -> None:
    """The visible Select uses one Eolas border rather than nested outlines."""

    stylesheet = Path(EolasApp.CSS_PATH).read_text(encoding="utf-8")

    assert "Select > SelectCurrent" in stylesheet
    assert "Input,\nSelect {" in stylesheet
    assert "border: solid $surface-ink;" in stylesheet
    assert "Select > SelectCurrent {\n    border: none;" in stylesheet
    assert "Select:focus > SelectCurrent" in stylesheet
    assert "border: solid $accent-focus;" in stylesheet


def testTuiStylesUseDistinctPrimarySuccessAndPanelBorders() -> None:
    """Eolas applies shared action hierarchy with its own palette."""

    stylesheet = Path(EolasApp.CSS_PATH).read_text(encoding="utf-8")

    assert "Button.-primary {\n    background: $accent;" in stylesheet
    assert "Button.-success {\n    background: $success-surface;" in stylesheet
    assert "$success-text: #d1aa5b;" in stylesheet
    assert ".summaryCard," in stylesheet
    assert "border: solid $border;" in stylesheet


def testTuiStylesPreserveSharedMockupLayout() -> None:
    """The project palette keeps the shared panel and mockup geometry."""

    stylesheet = Path(EolasApp.CSS_PATH).read_text(encoding="utf-8")

    assert ".surface {" in stylesheet
    assert ".mockup-row {" in stylesheet
    assert ".mockup-panel," in stylesheet
    assert "#style-mockup {" in stylesheet


def testTuiStylesKeepWarningListItemToOneRow() -> None:
    """The warning list label remains compact while warning panels are bordered."""

    stylesheet = Path(EolasApp.CSS_PATH).read_text(encoding="utf-8")

    assert ".warning {\n    background: $warning-surface;" in stylesheet
    assert "ListView .warning {\n    height: 1;" in stylesheet
    assert "padding: 0;\n    border: none;" in stylesheet


def testTuiStylesReplaceTextualBlueListHighlight() -> None:
    """Focused list selection uses the Eolas success palette."""

    stylesheet = Path(EolasApp.CSS_PATH).read_text(encoding="utf-8")

    assert "ListView:focus > ListItem.-highlight" in stylesheet
    assert "background: $success-surface;" in stylesheet
    assert "color: $success-text;" in stylesheet


def testTuiStylesUseCreamScrollbarThumb() -> None:
    """Scrollbars retain contrast against Eolas dark surfaces."""

    stylesheet = Path(EolasApp.CSS_PATH).read_text(encoding="utf-8")

    assert "scrollbar-color: $surface-ink;" in stylesheet
    assert "scrollbar-color-hover: $surface-ink;" in stylesheet
    assert "scrollbar-color-active: $surface-ink;" in stylesheet


def test_tuiNavigatesToCreateClann() -> None:
    """Create Clann is reached as an action within the Clann area."""

    async def exercise() -> None:
        app = EolasApp()
        async with app.run_test(size=(120, 40)) as pilot:
            await pilot.press("2")
            await pilot.pause()
            await _buttonActivate(app, pilot, "#clannCreate")

            view = app.query_one("#clannCreateView", ClannCreateView)
            assert view.display
            assert app.query_one("#pageTitle", Static).content == "Create a Clann"

    asyncio.run(exercise())


def test_tuiCreateClannUsesSharedService(
    tmp_path: Path,
    monkeypatch,
) -> None:
    """The TUI persists through the real shared Clann creation service."""

    monkeypatch.setattr(Path, "home", lambda: tmp_path)

    async def exercise() -> None:
        app = EolasApp()
        async with app.run_test(size=(120, 50)) as pilot:
            await pilot.press("2")
            await pilot.pause()
            await _buttonActivate(app, pilot, "#clannCreate")

            app.query_one("#clannName", Input).value = "Example Clann"
            app.query_one("#householdName", Input).value = "Family Home"
            app.query_one("#personFullName", Input).value = "Alex Example"
            app.query_one("#personPreferredName", Input).value = "Alex"
            app.query_one("#personRole", Input).value = "householder"

            await _buttonActivate(app, pilot, "#personAdd")

            table = app.query_one("#clannPeople", DataTable)
            assert table.row_count == 1

            await _buttonActivate(app, pilot, "#clannReview")
            await _modalButtonActivate(
                app,
                pilot,
                ClannCreateConfirmScreen,
                "#clannCreateConfirm",
            )

            assert (
                tmp_path / "eolas" / "clanns" / "example-clann" / "clann.yaml"
            ).is_file()
            status = app.query_one("#clannValidation", Static)
            assert "Clann created: Example Clann" in str(status.content)

    asyncio.run(exercise())


def test_tuiCreateClannRejectsIncompletePerson() -> None:
    """Person validation is supplied by the existing Clann domain model."""

    async def exercise() -> None:
        app = EolasApp()
        async with app.run_test(size=(120, 40)) as pilot:
            await pilot.press("2")
            await pilot.pause()
            await _buttonActivate(app, pilot, "#clannCreate")

            await _buttonActivate(app, pilot, "#personAdd")

            status = app.query_one("#personValidation", Static)
            assert "Person full name cannot be empty." in str(status.content)
            assert app.query_one("#clannPeople", DataTable).row_count == 0

    asyncio.run(exercise())



def test_eolasWithoutArgumentsLaunchesTui(monkeypatch) -> None:
    """The installed Eolas command opens the TUI when no CLI arguments are supplied."""

    import sys

    import eolas.cli as cliModule
    import eolas.tui.app as tuiModule

    launched = {"value": False}

    def tuiRunFake() -> int:
        launched["value"] = True
        return 0

    monkeypatch.setattr(tuiModule, "tuiRun", tuiRunFake)
    monkeypatch.setattr(sys, "argv", ["eolas"])

    assert cliModule.main() == 0
    assert launched["value"]


def test_eolasWithArgumentsUsesCli(monkeypatch) -> None:
    """Any supplied argument is dispatched through the CLI parser."""

    import sys

    import eolas.cli as cliModule

    received = []

    def cliRunFake(arguments=None) -> int:
        received.append(arguments)
        return 0

    monkeypatch.setattr(cliModule, "cliRun", cliRunFake)
    monkeypatch.setattr(sys, "argv", ["eolas", "log", "--show"])

    assert cliModule.main() == 0
    assert received == [["log", "--show"]]



def test_tuiSelectsActiveClann(
    tmp_path: Path,
    monkeypatch,
) -> None:
    """The Clann area establishes the active session Clann."""

    from eolas.clann.models import ClannInput, PersonInput
    from eolas.clann.service import clannCreate

    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    clannCreate(
        ClannInput(
            "Example Clann",
            "Family Home",
            [PersonInput("Alex Example", "Alex", "householder", True, True)],
        ),
        tmp_path / "eolas",
    )

    async def exercise() -> None:
        app = EolasApp()
        async with app.run_test(size=(120, 45)) as pilot:
            await pilot.press("2")
            await pilot.pause()

            available = app.query_one("#availableClanns", DataTable)
            assert available.row_count == 1

            await _buttonActivate(app, pilot, "#clannSwitch")

            status = app.query_one("#clannStatus", Static)
            assert "Active Clann: Example Clann" in str(status.content)
            navHint = app.query_one("#navHint", Static)
            assert "Example Clann" in str(navHint.content)

    asyncio.run(exercise())


def test_tuiQuickCapturePersistsToActiveClann(
    tmp_path: Path,
    monkeypatch,
) -> None:
    """Quick Capture prepares and writes through the shared capture services."""

    from eolas.clann.models import ClannInput, PersonInput
    from eolas.clann.service import clannCreate

    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    clannCreate(
        ClannInput(
            "Example Clann",
            "Family Home",
            [PersonInput("Alex Example", "Alex", "householder", True, True)],
        ),
        tmp_path / "eolas",
    )

    async def exercise() -> None:
        app = EolasApp()
        async with app.run_test(size=(140, 60)) as pilot:
            await pilot.press("2")
            await pilot.pause()
            await _buttonActivate(app, pilot, "#clannSwitch")

            await pilot.press("8")
            await pilot.pause()

            app.query_one("#captureDomain", Select).value = "banking"
            await _buttonActivate(app, pilot, "#captureFieldsLoad")

            app.query_one("#captureLabel", Input).value = "Household current account"
            app.query_one("#captureSource", Input).value = "Bank statement"

            values = {
                "institution": "Example Bank",
                "accountCategory": "current",
                "productName": "Current Account",
                "purpose": "Household bills",
                "owners": "Alex Example",
                "status": "active",
                "classification": "private",
                "lastReviewed": "2026-10-03",
            }
            for field, value in values.items():
                app.query_one(f"#captureField-{field}", Input).value = value

            await _buttonActivate(app, pilot, "#captureReview")
            await _modalButtonActivate(
                app,
                pilot,
                CaptureConfirmScreen,
                "#captureConfirm",
            )

            target = (
                tmp_path
                / "eolas"
                / "clanns"
                / "example-clann"
                / "shared"
                / "banking"
                / "household-current-account.yaml"
            )
            assert target.is_file()
            status = app.query_one("#captureValidation", Static)
            assert "Saved:" in str(status.content)

    asyncio.run(exercise())
