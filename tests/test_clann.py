"""Tests for Clann-rooted bootstrap generation."""

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

import pytest
import yaml
import tomllib

import eolas.clann.service as clannService
from eolas.clann.documents import (
    clannDocumentBuild,
    householdDocumentBuild,
    personDocumentBuild,
)
from eolas.clann.manifest import CLANN_DIRECTORIES
from eolas.clann.models import ClannInput, ClannValidationError, PersonInput
from eolas.clann.service import (
    ClannCreationError,
    ClannRepairError,
    clannCreate,
    clannRemoveIncomplete,
    clannRepair,
    clannRestoreIncomplete,
)
from eolas.clann.slugs import slugCreate, slugsCreateUnique
from eolas.clann.status import clannsRemoved
from eolas.cli import cliRun
from eolas.version import VERSION

TEST_TIME = datetime(2026, 7, 25, 14, 0, tzinfo=timezone.utc)


@pytest.fixture
def clann() -> ClannInput:
    return ClannInput(
        name="River Clann",
        primary_household_name="Family Home",
        people=[
            PersonInput("Morgan River", "Morgan", "householder", True, True),
            PersonInput("Jamie River", "Jamie", "family", False),
            PersonInput(
                "Alex River",
                "Alex",
                "family",
                True,
                lives_in_primary_household=False,
            ),
        ],
    )


def _yamlLoad(path: Path) -> Dict[str, Any]:
    loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(loaded, dict)
    return loaded


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("Wilson Clann", "wilson-clann"),
        ("O'Brien", "o-brien"),
        ("Élodie Brontë", "elodie-bronte"),
        ("../../unsafe", "unsafe"),
    ],
)
def test_slugCreate(value: str, expected: str) -> None:
    assert slugCreate(value) == expected


def test_slugsCreateUnique_suffixesDuplicateNames() -> None:
    assert slugsCreateUnique(["John Smith", "John Smith"]) == [
        "john-smith",
        "john-smith-2",
    ]


def test_clannValidate_requiresPrimaryPersonAndResident() -> None:
    withoutPrimary = ClannInput(
        "Test Clann",
        "Test Home",
        [PersonInput("Alex Test", "Alex", "adult", True)],
    )
    withoutResident = ClannInput(
        "Test Clann",
        "Test Home",
        [PersonInput("Alex Test", "Alex", "adult", True, True, False)],
    )

    with pytest.raises(ClannValidationError, match="exactly one"):
        withoutPrimary.clannValidate()
    with pytest.raises(ClannValidationError, match="at least one resident"):
        withoutResident.clannValidate()


def test_documentsKeepClannAndResidenceSeparate(clann: ClannInput) -> None:
    personIds = {
        0: "person-morgan-river",
        1: "person-jamie-river",
        2: "person-alex-river",
    }
    clannDocument = clannDocumentBuild(
        clann,
        "clann-river-clann",
        "household-family-home",
        personIds,
        TEST_TIME,
    )
    householdDocument = householdDocumentBuild(
        clann,
        "clann-river-clann",
        "household-family-home",
        personIds,
        TEST_TIME,
    )
    nonResidentDocument = personDocumentBuild(
        clann.people[2],
        personIds[2],
        "clann-river-clann",
        "household-family-home",
        TEST_TIME,
    )

    assert clannDocument["schema"] == "eolas/clann/v1"
    assert len(clannDocument["people"]) == 3
    assert clannDocument["primaryHouseholdRef"] == "household-family-home"
    assert len(householdDocument["members"]) == 2
    assert householdDocument["members"][0]["status"] == "resident"
    assert nonResidentDocument["clannRef"] == "clann-river-clann"
    assert nonResidentDocument["householdMemberships"] == []


def test_clannCreate_generatesCompleteReloadableTree(
    tmp_path: Path,
    clann: ClannInput,
) -> None:
    rootPath = clannCreate(
        clann, tmp_path / "data", timestampProvider=lambda: TEST_TIME
    )

    assert rootPath == tmp_path / "data" / "clanns" / "river-clann"
    assert (rootPath / "clann.yaml").is_file()
    for directoryName in CLANN_DIRECTORIES:
        assert (rootPath / directoryName).is_dir()
    householdPath = rootPath / "households" / "family-home" / "household.yaml"
    assert householdPath.is_file()

    documents = {path: _yamlLoad(path) for path in sorted(rootPath.rglob("*.yaml"))}
    assert len(documents) == 9
    clannDocument = documents[rootPath / "clann.yaml"]
    people = {
        document["id"]: document
        for path, document in documents.items()
        if path.name == "person.yaml"
    }
    householdDocument = documents[householdPath]

    assert {entry["personRef"] for entry in clannDocument["people"]} == set(people)
    assert all(person_id.startswith("rec_") for person_id in people)
    assert householdDocument["id"].startswith("rec_")
    residentIds = {member["personRef"] for member in householdDocument["members"]}
    assert len(residentIds) == 2
    nonResident = next(
        document
        for document in people.values()
        if document["name"]["displayName"] == "Alex River"
    )
    assert nonResident["householdMemberships"] == []
    for path in documents:
        assert path.read_bytes().endswith(b"\n")
        assert "!!python" not in path.read_text(encoding="utf-8")


def test_clannCreate_writesOpaquePeopleToRecordStore(
    tmp_path: Path,
    clann: ClannInput,
) -> None:
    from eolas.clann.records import clannRecordStoreOpen
    from eolas.domain.directory import peopleLoad
    from eolas.domain.values import identityOpaque

    rootPath = clannCreate(
        clann, tmp_path / "data", timestampProvider=lambda: TEST_TIME
    )
    store = clannRecordStoreOpen(rootPath, "clann-river-clann")
    people = peopleLoad(store)

    assert len(people) == 3
    assert {person.display_name for person in people} == {
        "Morgan River",
        "Jamie River",
        "Alex River",
    }
    assert all(identityOpaque(person.identity.record_id) for person in people)
    assert all(person.identity.aggregate_type == "person" for person in people)


def test_clannCreate_rejectsExistingNonEmptyTarget(
    tmp_path: Path, clann: ClannInput
) -> None:
    targetPath = tmp_path / "clanns" / "river-clann"
    targetPath.mkdir(parents=True)
    markerPath = targetPath / "keep.txt"
    markerPath.write_text("keep", encoding="utf-8")

    with pytest.raises(ClannCreationError, match="not empty"):
        clannCreate(clann, tmp_path)

    assert markerPath.read_text(encoding="utf-8") == "keep"


def test_clannCreate_failureLeavesNoPartialClann(
    tmp_path: Path,
    clann: ClannInput,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def treeFail(rootPath: Path, *_args: object) -> None:
        (rootPath / "partial.txt").write_text("partial", encoding="utf-8")
        raise OSError("injected failure")

    monkeypatch.setattr(clannService, "_clannTreeWrite", treeFail)

    with pytest.raises(OSError, match="injected failure"):
        clannCreate(clann, tmp_path / "data")

    assert not (tmp_path / "data").exists()


def test_cliCreatesClannThroughNaturalCommand(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    capturedClann = ClannInput(
        "Example Clann",
        "Family Home",
        [PersonInput("Alex Example", "Alex", "householder", True, True)],
    )
    monkeypatch.setattr("eolas.cli.clannCapture", lambda: capturedClann)
    monkeypatch.setattr(Path, "home", lambda: tmp_path)

    result = cliRun(["clann", "--create", "--confirm"])

    assert result == 0
    assert (tmp_path / "eolas/clanns/example-clann/clann.yaml").is_file()
    output = capsys.readouterr().out
    assert "Clann created:" in output
    assert "household role: householder; age: adult; residence: resident" in output


def testClannListShowsUsableClanns(
    tmp_path: Path, clann: ClannInput, monkeypatch, capsys
) -> None:
    rootPath = clannCreate(
        clann, tmp_path / "eolas", timestampProvider=lambda: TEST_TIME
    )
    monkeypatch.setattr(Path, "home", lambda: tmp_path)

    result = cliRun(["clann", "--list"])

    assert result == 0
    output = capsys.readouterr().out
    assert "River Clann (active; 3 people)" in output
    assert str(rootPath) not in output


def testClannStatusReportsIncompleteDirectories(
    tmp_path: Path, clann: ClannInput, monkeypatch, capsys
) -> None:
    clannCreate(clann, tmp_path / "eolas", timestampProvider=lambda: TEST_TIME)
    incomplete = tmp_path / "eolas/clanns/unfinished-clann"
    incomplete.mkdir()
    monkeypatch.setattr(Path, "home", lambda: tmp_path)

    result = cliRun(["clann", "--status"])

    assert result == 0
    output = capsys.readouterr().out
    assert "Usable Clanns: 1" in output
    assert "Directories needing attention:" in output
    assert "unfinished-clann: missing clann.yaml; run `eolas clann --repair`" in output


def testClannListExplainsWhenNoClannsExist(tmp_path: Path, monkeypatch, capsys) -> None:
    monkeypatch.setattr(Path, "home", lambda: tmp_path)

    assert cliRun(["clann", "--list"]) == 0

    assert "No usable Clanns found" in capsys.readouterr().out


def testClannListDirectsIncompleteClannToRepair(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    (tmp_path / "eolas/clanns/unfinished-clann").mkdir(parents=True)
    monkeypatch.setattr(Path, "home", lambda: tmp_path)

    assert cliRun(["clann", "--list"]) == 0

    assert "Run `eolas clann --repair`" in capsys.readouterr().out


def testClannCreateNormalisesUnambiguousHumanCasing(tmp_path: Path) -> None:
    created = clannCreate(
        ClannInput(
            "WILSON",
            "29A",
            [PersonInput("ANDY WILSON", "ANDY", "OWNER", True, True)],
        ),
        tmp_path,
        timestampProvider=lambda: TEST_TIME,
    )

    document = _yamlLoad(created / "clann.yaml")
    person = _yamlLoad(created / "people/andy-wilson/person.yaml")

    assert document["name"] == "Wilson"
    assert person["name"]["displayName"] == "Andy Wilson"
    assert person["name"]["preferredName"] == "Andy"
    assert person["householdMemberships"][0]["role"] == "Owner"


def testClannRepairCompletesPartialDirectory(tmp_path: Path, clann: ClannInput) -> None:
    targetPath = tmp_path / "eolas/clanns/river-clann"
    (targetPath / "contacts").mkdir(parents=True)
    (targetPath / "shared").mkdir()

    repairedPath = clannRepair(clann, targetPath, timestampProvider=lambda: TEST_TIME)

    assert repairedPath == targetPath
    assert (targetPath / "clann.yaml").is_file()
    assert (targetPath / "contacts").is_dir()
    assert (targetPath / "shared/records.yaml").is_file()


def testClannRepairRefusesFilesAndMismatchedNames(
    tmp_path: Path, clann: ClannInput
) -> None:
    targetPath = tmp_path / "eolas/clanns/river-clann"
    targetPath.mkdir(parents=True)
    (targetPath / "notes.txt").write_text("keep", encoding="utf-8")

    with pytest.raises(ClannRepairError, match="containing files"):
        clannRepair(clann, targetPath)

    (targetPath / "notes.txt").unlink()
    other = ClannInput(
        "Other Clann",
        "Family Home",
        [PersonInput("Alex Example", "Alex", "householder", True, True)],
    )
    with pytest.raises(ClannRepairError, match="must match"):
        clannRepair(other, targetPath)


def testClannRemoveIncompleteMovesOnlyNamedIncompleteDirectoryToWastebasket(
    tmp_path: Path, clann: ClannInput
) -> None:
    incompletePath = tmp_path / "eolas/clanns/wilson"
    incompletePath.mkdir(parents=True)
    usablePath = clannCreate(clann, tmp_path / "eolas", timestampProvider=lambda: TEST_TIME)

    clannRemoveIncomplete(tmp_path / "eolas", "wilson")

    assert not incompletePath.exists()
    assert (tmp_path / "eolas/clanns/.wastebasket/wilson").is_dir()
    assert (usablePath / "clann.yaml").is_file()
    with pytest.raises(ClannRepairError, match="usable Clann"):
        clannRemoveIncomplete(tmp_path / "eolas", usablePath.name)


def testClannRemoveIncompleteRejectsPathTraversal(tmp_path: Path) -> None:
    with pytest.raises(ClannRepairError, match="directory name only"):
        clannRemoveIncomplete(tmp_path / "eolas", "../other")


def testClannRestoreIncompleteMovesDirectoryBackToClanns(tmp_path: Path) -> None:
    incompletePath = tmp_path / "eolas/clanns/wilson"
    incompletePath.mkdir(parents=True)
    clannRemoveIncomplete(tmp_path / "eolas", "wilson")

    clannRestoreIncomplete(tmp_path / "eolas", "wilson")

    assert incompletePath.is_dir()
    assert not (tmp_path / "eolas/clanns/.wastebasket").exists()


def testClannsRemovedListsWastebasketDirectories(tmp_path: Path) -> None:
    firstPath = tmp_path / "eolas/clanns/first-clann"
    secondPath = tmp_path / "eolas/clanns/second-clann"
    firstPath.mkdir(parents=True)
    secondPath.mkdir()
    clannRemoveIncomplete(tmp_path / "eolas", firstPath.name)
    clannRemoveIncomplete(tmp_path / "eolas", secondPath.name)

    assert [path.name for path in clannsRemoved(tmp_path / "eolas")] == [
        "first-clann",
        "second-clann",
    ]


def testClannStatusIgnoresWastebasketDirectories(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    incompletePath = tmp_path / "eolas/clanns/wilson"
    incompletePath.mkdir(parents=True)
    clannRemoveIncomplete(tmp_path / "eolas", "wilson")
    monkeypatch.setattr(Path, "home", lambda: tmp_path)

    assert cliRun(["clann", "--status"]) == 0

    output = capsys.readouterr().out
    assert "Usable Clanns: 0" in output
    assert "Directories needing attention:" not in output
    assert ".wastebasket" not in output


def testCliRepairCompletesPartialDirectory(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    targetPath = tmp_path / "eolas/clanns/example-clann"
    targetPath.mkdir(parents=True)
    captured = ClannInput(
        "Example Clann",
        "Example Home",
        [PersonInput("Alex Example", "Alex", "householder", True, True)],
    )
    monkeypatch.setattr("eolas.cli.clannCapture", lambda: captured)

    result = cliRun(["clann", "--repair", str(targetPath), "--confirm"])

    assert result == 0
    assert (targetPath / "clann.yaml").is_file()
    output = capsys.readouterr().out
    assert "Checking" in output
    assert "No readable bootstrap records were found" in output
    assert "Clann repaired:" in output


def testCliRepairSelectsSoleIncompleteDirectory(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    targetPath = tmp_path / "eolas/clanns/example-clann"
    targetPath.mkdir(parents=True)
    captured = ClannInput(
        "Example Clann",
        "Example Home",
        [PersonInput("Alex Example", "Alex", "householder", True, True)],
    )
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    monkeypatch.setattr("eolas.cli.clannCapture", lambda: captured)

    result = cliRun(["clann", "--repair", "--confirm"])

    assert result == 0
    assert (targetPath / "clann.yaml").is_file()
    assert "Clann repaired:" in capsys.readouterr().out


def testCliRepairListsAndChoosesIncompleteDirectories(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    firstPath = tmp_path / "eolas/clanns/first-clann"
    secondPath = tmp_path / "eolas/clanns/second-clann"
    firstPath.mkdir(parents=True)
    secondPath.mkdir()
    captured = ClannInput(
        "Second Clann",
        "Example Home",
        [PersonInput("Alex Example", "Alex", "householder", True, True)],
    )
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    monkeypatch.setattr("eolas.cli.clannCapture", lambda: captured)
    monkeypatch.setattr("eolas.cli.clannPathCapture", lambda _paths: secondPath)

    result = cliRun(["clann", "--repair", "--confirm"])

    assert result == 0
    assert (secondPath / "clann.yaml").is_file()
    output = capsys.readouterr().out
    assert "Incomplete Clann directories:" in output
    assert "first-clann: missing clann.yaml" in output
    assert "second-clann: missing clann.yaml" in output


def testCliRemoveConfirmsBeforeDeletingIncompleteDirectory(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    targetPath = tmp_path / "eolas/clanns/wilson"
    targetPath.mkdir(parents=True)
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    monkeypatch.setattr("eolas.cli.confirmationCapture", lambda *_args, **_kwargs: True)

    result = cliRun(["clann", "--remove", "wilson"])

    assert result == 0
    assert not targetPath.exists()
    assert (
        tmp_path / "eolas/clanns/.wastebasket/wilson"
    ).is_dir()
    assert "Moved incomplete Clann directory to the wastebasket" in capsys.readouterr().out


def testCliRemoveCancellationPreservesIncompleteDirectory(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    targetPath = tmp_path / "eolas/clanns/wilson"
    targetPath.mkdir(parents=True)
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    monkeypatch.setattr("eolas.cli.confirmationCapture", lambda *_args, **_kwargs: False)

    result = cliRun(["clann", "--remove", "wilson"])

    assert result == 0
    assert targetPath.is_dir()
    assert "Clann removal cancelled" in capsys.readouterr().out


def testCliRemoveConfirmFlagBypassesConfirmation(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    targetPath = tmp_path / "eolas/clanns/wilson"
    targetPath.mkdir(parents=True)
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    monkeypatch.setattr(
        "eolas.cli.confirmationCapture",
        lambda *_args, **_kwargs: pytest.fail("confirmation should be bypassed"),
    )

    assert cliRun(["clann", "--remove", "wilson", "-y"]) == 0

    assert (tmp_path / "eolas/clanns/.wastebasket/wilson").is_dir()


def testCliRestoreConfirmsBeforeMovingIncompleteDirectoryBack(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    targetPath = tmp_path / "eolas/clanns/wilson"
    targetPath.mkdir(parents=True)
    clannRemoveIncomplete(tmp_path / "eolas", "wilson")
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    monkeypatch.setattr("eolas.cli.confirmationCapture", lambda *_args, **_kwargs: True)

    result = cliRun(["clann", "--restore", "wilson"])

    assert result == 0
    assert targetPath.is_dir()
    assert "Restored incomplete Clann directory: wilson" in capsys.readouterr().out


def testCliRestoreListsAndChoosesRemovedDirectories(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    firstPath = tmp_path / "eolas/clanns/first-clann"
    secondPath = tmp_path / "eolas/clanns/second-clann"
    firstPath.mkdir(parents=True)
    secondPath.mkdir()
    clannRemoveIncomplete(tmp_path / "eolas", firstPath.name)
    clannRemoveIncomplete(tmp_path / "eolas", secondPath.name)
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    monkeypatch.setattr(
        "eolas.cli.clannPathCapture",
        lambda _paths: tmp_path / "eolas/clanns/.wastebasket/second-clann",
    )

    result = cliRun(["clann", "--restore", "-y"])

    assert result == 0
    assert firstPath.parent.joinpath(".wastebasket", firstPath.name).is_dir()
    assert secondPath.is_dir()
    output = capsys.readouterr().out
    assert "Removed incomplete Clann directories:" in output
    assert "- first-clann" in output
    assert "- second-clann" in output


def testCliVersionUsesPackageVersion(
    capsys: pytest.CaptureFixture[str],
) -> None:
    with pytest.raises(SystemExit) as error:
        cliRun(["--version"])

    assert error.value.code == 0
    assert capsys.readouterr().out == f"eolas {VERSION}\n"


def testPackageMetadataUsesVersionModule() -> None:
    project = tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))[
        "project"
    ]
    dynamic = project["dynamic"]

    assert "version" in dynamic
    assert VERSION == "0.2a1"


def test_cliShowsLogFile(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    logPath = tmp_path / "eolas" / "eolas.log"
    logPath.parent.mkdir()
    logPath.write_text("Eolas started\n", encoding="utf-8")
    monkeypatch.setattr(Path, "home", lambda: tmp_path)

    result = cliRun(["log", "--show"])

    assert result == 0
    assert capsys.readouterr().out == "Eolas started\n"


def test_cliReportsMissingLogFile(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr(Path, "home", lambda: tmp_path)

    result = cliRun(["log", "--show"])

    assert result == 1
    assert "No Eolas log file found:" in capsys.readouterr().out
