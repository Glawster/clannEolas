"""Interaction tests for the Textual Eolas terminal interface."""

import asyncio
from pathlib import Path

from textual.widgets import DataTable, Input, Static

from eolas.tui.app import EolasApp
from eolas.tui.views.clannCreate import ClannCreateView


def test_tuiNavigatesToCreateClann() -> None:
    """The production shell exposes Create Clann through keyboard navigation."""

    async def exercise() -> None:
        app = EolasApp()
        async with app.run_test(size=(120, 40)) as pilot:
            await pilot.press("9")
            await pilot.pause()

            view = app.query_one("#clannCreateView", ClannCreateView)
            assert view.display
            assert app.query_one("#pageTitle", Static).renderable == "Create a Clann"

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
            await pilot.press("9")
            await pilot.pause()

            app.query_one("#clannName", Input).value = "Example Clann"
            app.query_one("#householdName", Input).value = "Family Home"
            app.query_one("#personFullName", Input).value = "Alex Example"
            app.query_one("#personPreferredName", Input).value = "Alex"
            app.query_one("#personRole", Input).value = "householder"

            await pilot.click("#personAdd")
            await pilot.pause()

            table = app.query_one("#clannPeople", DataTable)
            assert table.row_count == 1

            await pilot.click("#clannReview")
            await pilot.pause()
            await pilot.click("#clannCreateConfirm")
            await pilot.pause()

            assert (
                tmp_path / "eolas" / "clanns" / "example-clann" / "clann.yaml"
            ).is_file()
            status = app.query_one("#clannValidation", Static)
            assert "Clann created: Example Clann" in str(status.renderable)

    asyncio.run(exercise())


def test_tuiCreateClannRejectsIncompletePerson() -> None:
    """Person validation is supplied by the existing Clann domain model."""

    async def exercise() -> None:
        app = EolasApp()
        async with app.run_test(size=(120, 40)) as pilot:
            await pilot.press("9")
            await pilot.pause()

            await pilot.click("#personAdd")
            await pilot.pause()

            status = app.query_one("#personValidation", Static)
            assert "Person full name cannot be empty." in str(status.renderable)
            assert app.query_one("#clannPeople", DataTable).row_count == 0

    asyncio.run(exercise())
