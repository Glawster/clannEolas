"""Atomic Clann creation service."""

import shutil
import tempfile
import os
from datetime import datetime
from pathlib import Path
from typing import Callable, Dict, Optional

from eolas.clann.documents import (
    clannDocumentBuild,
    householdDocumentBuild,
    identityDocumentBuild,
    personDocumentBuild,
)
from eolas.clann.manifest import CLANN_DIRECTORIES, PERSON_SECTIONS
from eolas.clann.models import ClannInput, clannNormalise
from eolas.clann.records import RECORDS_RELATIVE
from eolas.clann.slugs import slugCreate, slugsCreateUnique
from eolas.clann.yaml_io import yamlWrite
from eolas.domain.codec import personEncode
from eolas.domain.entities import Person
from eolas.domain.storage import WriteOperation, YamlRecordStore
from eolas.domain.values import Classification, RecordIdentity


class ClannCreationError(RuntimeError):
    """Raised when a Clann cannot be safely created."""


class ClannRepairError(RuntimeError):
    """Raised when an incomplete Clann directory cannot be safely repaired."""


TimestampProvider = Callable[[], datetime]


def clannCreate(
    clann: ClannInput,
    outputDirectory: Path,
    *,
    timestampProvider: Optional[TimestampProvider] = None,
) -> Path:
    """Validate and atomically create ``clanns/<slug>`` under a data root."""

    clann = clannNormalise(clann)
    clann.clannValidate()
    outputDirectory = outputDirectory.expanduser().resolve()
    if outputDirectory.exists() and not outputDirectory.is_dir():
        raise ClannCreationError(f"Output path is not a directory: {outputDirectory}")

    clannsPath = outputDirectory / "clanns"
    clannsPath.mkdir(parents=True, exist_ok=True)
    clannSlug = slugCreate(clann.name)
    targetPath = clannsPath / clannSlug
    if targetPath.exists() and any(targetPath.iterdir()):
        raise ClannCreationError(
            f"Target directory already exists and is not empty: {targetPath}. "
            "Choose a different Clann name or output directory."
        )

    provider = timestampProvider or (lambda: datetime.now().astimezone())
    timestamp = provider()
    if timestamp.tzinfo is None or timestamp.utcoffset() is None:
        raise ClannCreationError(
            "Timestamp provider must return a timezone-aware value."
        )

    personSlugs = slugsCreateUnique(person.full_name for person in clann.people)
    clannId = f"clann-{clannSlug}"
    householdSlug = slugCreate(clann.primary_household_name)
    householdId = RecordIdentity.identityCreate(
        clannId, "household", "shared"
    ).record_id
    personIds: Dict[int, str] = {
        index: RecordIdentity.identityCreate(clannId, "person", "shared").record_id
        for index in range(len(clann.people))
    }

    temporaryPath = Path(tempfile.mkdtemp(prefix=f".{clannSlug}-", dir=clannsPath))
    try:
        _clannTreeWrite(
            temporaryPath,
            clann,
            clannId,
            householdId,
            householdSlug,
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
        if clannsPath.exists() and not any(clannsPath.iterdir()):
            clannsPath.rmdir()
        if outputDirectory.exists() and not any(outputDirectory.iterdir()):
            outputDirectory.rmdir()
        raise

    return targetPath


def clannRepair(
    clann: ClannInput,
    targetPath: Path,
    *,
    timestampProvider: Optional[TimestampProvider] = None,
) -> Path:
    """Complete an empty partial Clann directory without overwriting its files."""
    clann = clannNormalise(clann)
    clann.clannValidate()
    targetPath = targetPath.expanduser().resolve()
    _repairTargetValidate(targetPath, clann)

    temporaryParent = Path(
        tempfile.mkdtemp(prefix=f".{targetPath.name}-repair-", dir=targetPath.parent)
    )
    createdPaths: list[Path] = []
    createdDirectories: list[Path] = []
    try:
        stagedPath = clannCreate(
            clann, temporaryParent, timestampProvider=timestampProvider
        )
        for sourcePath in sorted(stagedPath.rglob("*")):
            relativePath = sourcePath.relative_to(stagedPath)
            destinationPath = targetPath / relativePath
            if sourcePath.is_dir():
                if not destinationPath.exists():
                    destinationPath.mkdir()
                    createdDirectories.append(destinationPath)
                continue
            if destinationPath.exists():
                raise ClannRepairError(
                    f"Repair would overwrite existing file: {destinationPath}"
                )
            destinationPath.parent.mkdir(parents=True, exist_ok=True)
            os.link(sourcePath, destinationPath)
            createdPaths.append(destinationPath)
    except BaseException:
        for path in reversed(createdPaths):
            path.unlink(missing_ok=True)
        for path in reversed(createdDirectories):
            path.rmdir()
        raise
    finally:
        shutil.rmtree(temporaryParent)
    return targetPath


def clannRemoveIncomplete(dataRoot: Path, directoryName: str) -> None:
    """Move one explicitly named incomplete Clann directory to the wastebasket."""
    clannsPath, targetPath = _incompleteTargetGet(dataRoot, directoryName)
    if targetPath.parent != clannsPath or not targetPath.is_dir():
        raise ClannRepairError(f"No incomplete Clann directory named: {directoryName}")
    if (targetPath / "clann.yaml").is_file():
        raise ClannRepairError(
            f"{directoryName} is a usable Clann and cannot be removed with this command."
        )

    wastebasketPath = clannsPath / ".wastebasket"
    destinationPath = wastebasketPath / directoryName
    if destinationPath.exists():
        raise ClannRepairError(
            f"A removed incomplete Clann named {directoryName} already exists."
        )
    wastebasketPath.mkdir(exist_ok=True)
    targetPath.rename(destinationPath)


def clannRestoreIncomplete(dataRoot: Path, directoryName: str) -> None:
    """Restore one named incomplete Clann directory from the wastebasket."""
    clannsPath, targetPath = _incompleteTargetGet(dataRoot, directoryName)
    sourcePath = clannsPath / ".wastebasket" / directoryName
    if not sourcePath.is_dir():
        raise ClannRepairError(f"No removed incomplete Clann directory named: {directoryName}")
    if targetPath.exists():
        raise ClannRepairError(
            f"Cannot restore {directoryName} because a Clann directory already exists."
        )

    sourcePath.rename(targetPath)
    wastebasketPath = sourcePath.parent
    if not any(wastebasketPath.iterdir()):
        wastebasketPath.rmdir()


def _repairTargetValidate(targetPath: Path, clann: ClannInput) -> None:
    """Reject any repair that might overwrite data or create a mismatched Clann."""
    if not targetPath.is_dir():
        raise ClannRepairError(
            f"Repair directory does not exist: {targetPath}. "
            "Use `eolas clann --create` for a new Clann."
        )
    if targetPath.parent.name != "clanns":
        raise ClannRepairError(
            "Repair directory must be directly beneath the Eolas clanns directory."
        )
    if (targetPath / "clann.yaml").exists():
        raise ClannRepairError(
            f"Repair directory already contains clann.yaml: {targetPath}"
        )
    if slugCreate(clann.name) != targetPath.name:
        raise ClannRepairError(
            "The entered Clann name must match the repair directory name."
        )
    existingFiles = [path for path in targetPath.rglob("*") if path.is_file()]
    if existingFiles:
        raise ClannRepairError(
            "Repair refuses folders containing files because it cannot safely "
            "infer or overwrite existing data."
        )


def _incompleteTargetGet(dataRoot: Path, directoryName: str) -> tuple[Path, Path]:
    """Validate a single directory name and resolve its private Clann path."""
    if not directoryName or Path(directoryName).name != directoryName:
        raise ClannRepairError("Provide the incomplete Clann directory name only.")
    clannsPath = (dataRoot.expanduser().resolve() / "clanns").resolve()
    targetPath = (clannsPath / directoryName).resolve()
    if targetPath.parent != clannsPath:
        raise ClannRepairError("Provide the incomplete Clann directory name only.")
    return clannsPath, targetPath


def _clannTreeWrite(
    rootPath: Path,
    clann: ClannInput,
    clannId: str,
    householdId: str,
    householdSlug: str,
    personSlugs: list[str],
    personIds: Dict[int, str],
    timestamp: datetime,
) -> None:
    """Build all content beneath an isolated temporary root."""

    for directoryName in CLANN_DIRECTORIES:
        (rootPath / directoryName).mkdir()

    yamlWrite(
        rootPath / "clann.yaml",
        clannDocumentBuild(clann, clannId, householdId, personIds, timestamp),
    )

    householdPath = rootPath / "households" / householdSlug
    householdPath.mkdir()
    yamlWrite(
        householdPath / "household.yaml",
        householdDocumentBuild(clann, clannId, householdId, personIds, timestamp),
    )

    for index, person in enumerate(clann.people):
        personPath = rootPath / "people" / personSlugs[index]
        personPath.mkdir()
        personId = personIds[index]
        yamlWrite(
            personPath / "person.yaml",
            personDocumentBuild(person, personId, clannId, householdId, timestamp),
        )
        yamlWrite(
            personPath / PERSON_SECTIONS["identity"]["filename"],
            identityDocumentBuild(person, personId, timestamp),
        )

    _peopleStoreWrite(rootPath, clann, clannId, personIds)


def _peopleStoreWrite(
    rootPath: Path,
    clann: ClannInput,
    clannId: str,
    personIds: Dict[int, str],
) -> None:
    """Persist Person aggregates through the shared RecordStore port."""
    store = YamlRecordStore(rootPath / RECORDS_RELATIVE, clannId)
    operations = tuple(
        WriteOperation(
            personEncode(
                Person(
                    RecordIdentity(personIds[index], clannId, "person", "shared"),
                    person.full_name.strip(),
                    Classification.PRIVATE,
                )
            ),
            None,
        )
        for index, person in enumerate(clann.people)
    )
    store.recordsCommit(operations)
