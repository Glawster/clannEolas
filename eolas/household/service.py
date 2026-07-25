"""Atomic household creation service."""

import shutil
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Callable, Dict, Optional

from eolas.household.documents import (
    householdDocumentBuild,
    identityDocumentBuild,
    personDocumentBuild,
)
from eolas.household.manifest import HOUSEHOLD_DIRECTORIES, PERSON_SECTIONS
from eolas.household.models import HouseholdInput
from eolas.household.slugs import slugCreate, slugsCreateUnique
from eolas.household.yaml_io import yamlWrite


class HouseholdCreationError(RuntimeError):
    """Raised when a household cannot be safely created."""


TimestampProvider = Callable[[], datetime]


def householdCreate(
    household: HouseholdInput,
    outputDirectory: Path,
    *,
    timestampProvider: Optional[TimestampProvider] = None,
) -> Path:
    """Validate and atomically create a household data directory."""

    household.householdValidate()
    outputDirectory = outputDirectory.expanduser().resolve()
    if outputDirectory.exists() and not outputDirectory.is_dir():
        raise HouseholdCreationError(
            f"Output path is not a directory: {outputDirectory}"
        )
    outputDirectory.mkdir(parents=True, exist_ok=True)

    householdSlug = slugCreate(household.name)
    targetPath = outputDirectory / householdSlug
    if targetPath.exists() and any(targetPath.iterdir()):
        raise HouseholdCreationError(
            f"Target directory already exists and is not empty: {targetPath}. "
            "Choose a different household name or output directory."
        )

    provider = timestampProvider or (lambda: datetime.now().astimezone())
    timestamp = provider()
    if timestamp.tzinfo is None or timestamp.utcoffset() is None:
        raise HouseholdCreationError(
            "Timestamp provider must return a timezone-aware value."
        )

    personSlugs = slugsCreateUnique(member.full_name for member in household.members)
    householdId = f"household-{householdSlug}"
    personIds: Dict[int, str] = {
        index: f"person-{personSlug}" for index, personSlug in enumerate(personSlugs)
    }

    temporaryPath = Path(
        tempfile.mkdtemp(prefix=f".{householdSlug}-", dir=outputDirectory)
    )
    try:
        _householdTreeWrite(
            temporaryPath,
            household,
            householdId,
            personSlugs,
            personIds,
            timestamp,
        )
        if targetPath.exists():
            targetPath.rmdir()
        temporaryPath.rename(targetPath)
    except BaseException:
        if temporaryPath.exists():
            shutil.rmtree(temporaryPath)
        raise

    return targetPath


def _householdTreeWrite(
    rootPath: Path,
    household: HouseholdInput,
    householdId: str,
    personSlugs: list[str],
    personIds: Dict[int, str],
    timestamp: datetime,
) -> None:
    """Build all content beneath an isolated temporary root."""

    peoplePath = rootPath / "people"
    peoplePath.mkdir()
    for directoryName in HOUSEHOLD_DIRECTORIES:
        (rootPath / directoryName).mkdir()

    yamlWrite(
        rootPath / "household.yaml",
        householdDocumentBuild(household, householdId, personIds, timestamp),
    )

    for index, person in enumerate(household.members):
        personPath = peoplePath / personSlugs[index]
        personPath.mkdir()
        personId = personIds[index]
        yamlWrite(
            personPath / "person.yaml",
            personDocumentBuild(person, personId, householdId, timestamp),
        )
        yamlWrite(
            personPath / PERSON_SECTIONS["identity"]["filename"],
            identityDocumentBuild(person, personId, timestamp),
        )
