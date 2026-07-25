"""Tests for household bootstrap generation."""

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

import pytest
import yaml

import eolas.household.service as householdService
from eolas.household.documents import (
    householdDocumentBuild,
    identityDocumentBuild,
    personDocumentBuild,
)
from eolas.household.manifest import HOUSEHOLD_DIRECTORIES
from eolas.household.models import (
    HouseholdInput,
    HouseholdValidationError,
    PersonInput,
)
from eolas.household.names import nameParse
from eolas.household.service import HouseholdCreationError, householdCreate
from eolas.household.slugs import slugCreate, slugsCreateUnique

TEST_TIME = datetime(2026, 7, 25, 14, 0, tzinfo=timezone.utc)


@pytest.fixture
def household() -> HouseholdInput:
    """Return a fictional two-person household."""

    return HouseholdInput(
        name="River Household",
        members=[
            PersonInput("Morgan River", "Morgan", "self", True, True),
            PersonInput("Jamie River", "Jamie", "child", False),
        ],
    )


def _yamlLoad(path: Path) -> Dict[str, Any]:
    with path.open(encoding="utf-8") as stream:
        loaded = yaml.safe_load(stream)
    assert isinstance(loaded, dict)
    return loaded


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("Wilson Family", "wilson-family"),
        ("Hello, world!", "hello-world"),
        ("O'Brien", "o-brien"),
        ("many   spaces", "many-spaces"),
        ("Élodie Brontë", "elodie-bronte"),
        ("../../unsafe", "unsafe"),
    ],
)
def test_slugCreate(value: str, expected: str) -> None:
    assert slugCreate(value) == expected


@pytest.mark.parametrize("value", ["", "   ", "!!!", "💚"])
def test_slugCreate_rejectsEmptyResult(value: str) -> None:
    with pytest.raises(ValueError):
        slugCreate(value)


def test_slugsCreateUnique_suffixesDuplicatesDeterministically() -> None:
    assert slugsCreateUnique(["John Smith", "John Smith", "John Smith"]) == [
        "john-smith",
        "john-smith-2",
        "john-smith-3",
    ]


def test_householdValidate_requiresExactlyOnePrimary() -> None:
    withoutPrimary = HouseholdInput(
        "Test",
        [PersonInput("Alex Test", "Alex", "self", True)],
    )
    withTwoPrimaries = HouseholdInput(
        "Test",
        [
            PersonInput("Alex Test", "Alex", "self", True, True),
            PersonInput("Sam Test", "Sam", "partner", True, True),
        ],
    )

    with pytest.raises(HouseholdValidationError, match="exactly one"):
        withoutPrimary.householdValidate()
    with pytest.raises(HouseholdValidationError, match="exactly one"):
        withTwoPrimaries.householdValidate()


@pytest.mark.parametrize(
    "household",
    [
        HouseholdInput(
            "",
            [PersonInput("Alex Test", "Alex", "self", True, True)],
        ),
        HouseholdInput("Test", []),
        HouseholdInput(
            "Test",
            [PersonInput("", "Alex", "self", True, True)],
        ),
    ],
)
def test_householdValidate_rejectsInvalidInput(
    household: HouseholdInput,
) -> None:
    with pytest.raises(HouseholdValidationError):
        household.householdValidate()


def test_nameParse_parsesSimpleFullName() -> None:
    parsed = nameParse("Mary Jane van Smith")
    assert parsed.first_name == "Mary"
    assert parsed.middle_names == ["Jane", "van"]
    assert parsed.last_name == "Smith"


def test_nameParse_acceptsSingleTokenName() -> None:
    parsed = nameParse("Cher")
    assert parsed.first_name == "Cher"
    assert parsed.middle_names == []
    assert parsed.last_name is None


def test_householdDocumentBuild_hasExpectedContent(
    household: HouseholdInput,
) -> None:
    document = householdDocumentBuild(
        household,
        "household-river-household",
        {0: "person-morgan-river", 1: "person-jamie-river"},
        TEST_TIME,
    )
    assert document["schema"] == "eolas/household/v1"
    assert document["primaryPersonRef"] == "person-morgan-river"
    assert document["members"][1] == {
        "personRef": "person-jamie-river",
        "role": "child",
    }
    assert document["metadata"]["created"] == TEST_TIME.isoformat()
    assert document["metadata"]["lastReviewed"] is None


def test_personDocumentBuild_hasExpectedContent(
    household: HouseholdInput,
) -> None:
    document = personDocumentBuild(
        household.members[0],
        "person-morgan-river",
        "household-river-household",
        TEST_TIME,
    )
    assert document["schema"] == "eolas/person/v1"
    assert document["name"]["displayName"] == "Morgan River"
    assert document["role"]["isAdult"] is True
    assert document["role"]["isPrimary"] is True
    assert document["sections"] == {"identity": "identity.yaml"}


def test_identityDocumentBuild_hasExpectedContent(
    household: HouseholdInput,
) -> None:
    document = identityDocumentBuild(
        household.members[0],
        "person-morgan-river",
        TEST_TIME,
    )
    assert document["schema"] == "eolas/person/identity/v1"
    assert document["personal"]["firstName"] == "Morgan"
    assert document["personal"]["lastName"] == "River"
    assert document["identifiers"]["nhsNumber"] is None
    assert document["documents"]["lastingPowerOfAttorneyRefs"] == []


def test_householdCreate_generatesCompleteReloadableTree(
    tmp_path: Path,
    household: HouseholdInput,
) -> None:
    rootPath = householdCreate(
        household,
        tmp_path,
        timestampProvider=lambda: TEST_TIME,
    )

    assert rootPath == tmp_path / "river-household"
    assert (rootPath / "household.yaml").is_file()
    for directoryName in HOUSEHOLD_DIRECTORIES:
        assert (rootPath / directoryName).is_dir()

    yamlPaths = sorted(rootPath.rglob("*.yaml"))
    assert len(yamlPaths) == 5
    documents = {path: _yamlLoad(path) for path in yamlPaths}
    householdDocument = documents[rootPath / "household.yaml"]

    peopleById: Dict[str, Path] = {}
    primaryCount = 0
    for personPath in sorted((rootPath / "people").iterdir()):
        personDocument = documents[personPath / "person.yaml"]
        peopleById[personDocument["id"]] = personPath
        primaryCount += int(personDocument["role"]["isPrimary"])
        for sectionPath in personDocument["sections"].values():
            assert (personPath / sectionPath).is_file()
        identityDocument = documents[personPath / "identity.yaml"]
        assert identityDocument["personRef"] == personDocument["id"]

    assert primaryCount == 1
    for member in householdDocument["members"]:
        assert member["personRef"] in peopleById
    assert householdDocument["primaryPersonRef"] in peopleById

    for path in yamlPaths:
        assert path.read_bytes().endswith(b"\n")
        assert "!!python" not in path.read_text(encoding="utf-8")


def test_householdCreate_handlesDuplicateNames(tmp_path: Path) -> None:
    household = HouseholdInput(
        "Duplicate Household",
        [
            PersonInput("John Smith", "John", "self", True, True),
            PersonInput("John Smith", "Johnny", "relative", True),
        ],
    )
    rootPath = householdCreate(household, tmp_path)

    assert (rootPath / "people" / "john-smith").is_dir()
    assert (rootPath / "people" / "john-smith-2").is_dir()
    ids = {
        _yamlLoad(path)["id"] for path in (rootPath / "people").glob("*/person.yaml")
    }
    assert ids == {"person-john-smith", "person-john-smith-2"}


def test_householdCreate_rejectsExistingNonEmptyTarget(
    tmp_path: Path,
    household: HouseholdInput,
) -> None:
    targetPath = tmp_path / "river-household"
    targetPath.mkdir()
    markerPath = targetPath / "keep.txt"
    markerPath.write_text("keep", encoding="utf-8")

    with pytest.raises(HouseholdCreationError, match="not empty"):
        householdCreate(household, tmp_path)

    assert markerPath.read_text(encoding="utf-8") == "keep"


def test_householdCreate_failureLeavesNoPartialOutput(
    tmp_path: Path,
    household: HouseholdInput,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def treeFail(rootPath: Path, *_args: object) -> None:
        (rootPath / "partial.txt").write_text("partial", encoding="utf-8")
        raise OSError("injected failure")

    monkeypatch.setattr(householdService, "_householdTreeWrite", treeFail)

    with pytest.raises(OSError, match="injected failure"):
        householdCreate(household, tmp_path)

    assert list(tmp_path.iterdir()) == []


def test_householdCreate_rejectsNaiveTimestamp(
    tmp_path: Path,
    household: HouseholdInput,
) -> None:
    with pytest.raises(HouseholdCreationError, match="timezone-aware"):
        householdCreate(
            household,
            tmp_path,
            timestampProvider=lambda: datetime(2026, 7, 25),
        )
    assert list(tmp_path.iterdir()) == []
