"""Command-line interface for Eolas."""

import argparse
import sys
from pathlib import Path
from typing import Any, List, Mapping, Optional, Sequence

import yaml

from eolas.capture.models import CAPTURE_PROFILES, CaptureInput, CaptureValidationError
from eolas.capture.service import CaptureWriteError, capturePrepare, captureWrite
from eolas.clann.models import ClannInput, ClannValidationError, PersonInput
from eolas.clann.service import ClannCreationError, clannCreate
from eolas.clann.slugs import slugCreate
from eolas.curses_ui import (
    CursesCancelled,
    captureDomainCapture,
    clannCapture,
    clannPathCapture,
    confirmationCapture,
    domainCapture,
)

ROLE_SUGGESTIONS = "householder, partner, family, carer, lodger, other"


def main() -> int:
    """Run the installed ``eolas`` console command."""
    return cliRun()


def cliRun(arguments: Optional[Sequence[str]] = None) -> int:
    """Parse and run an Eolas command."""

    parser = _parserBuild()
    args = parser.parse_args(arguments)
    if args.area == "clann" and args.action == "create":
        return _clannAsk(confirm=args.confirm)
    if args.area == "capture":
        return _captureRun(args)
    if args.area == "log" and args.action == "show":
        return _logShow()
    parser.print_help()
    return 0


def _confirmationAsk(prompt: str, *, default: bool) -> bool:
    suffix = " [Y/n]: " if default else " [y/N]: "
    while True:
        answer = input(prompt + suffix).strip().lower()
        if not answer:
            return default
        if answer in {"y", "yes"}:
            return True
        if answer in {"n", "no"}:
            return False
        print("Please answer yes or no.")


def _clannAsk(*, confirm: bool) -> int:
    try:
        clann = clannCapture()
        outputDirectory = _dataRootGet()
        clann.clannValidate()
        targetPath = outputDirectory / "clanns" / slugCreate(clann.name)
        _summaryPrint(clann, targetPath)
        if not confirm and not confirmationCapture(
            "Generate these files?", default=True
        ):
            print("Clann setup cancelled; no files were created.")
            return 0
        createdPath = clannCreate(clann, outputDirectory)
    except (CursesCancelled, EOFError, KeyboardInterrupt):
        print("\nClann setup cancelled; no files were created.")
        return 130
    except (ClannCreationError, ClannValidationError, OSError, ValueError) as error:
        _statusPrint(f"Error: {error}", colour="red")
        return 1

    residentCount = sum(person.lives_in_primary_household for person in clann.people)
    _statusPrint(f"\nClann created: {createdPath}", colour="green")
    print(f"People created: {len(clann.people)}")
    print(f"Primary household residents: {residentCount}")
    return 0


def _peopleAsk(personCount: int, *, resident: bool) -> List[PersonInput]:
    people: List[PersonInput] = []
    for index in range(personCount):
        location = "resident" if resident else "non-resident Clann person"
        print(f"\n{location.title()} {index + 1} of {personCount}")
        fullName = _requiredAsk("  Full name: ")
        preferredName = _requiredAsk("  Preferred name: ")
        print(f"  Suggested practical roles: {ROLE_SUGGESTIONS}")
        householdRole = _requiredAsk("  Household role: ")
        isAdult = _confirmationAsk("  Is this person legally an adult?", default=True)
        people.append(
            PersonInput(
                full_name=fullName,
                preferred_name=preferredName,
                household_role=householdRole,
                is_adult=isAdult,
                lives_in_primary_household=resident,
            )
        )
    return people


def _dataRootGet() -> Path:
    """Return the private Eolas data root beneath the current user's home."""
    return Path.home() / "eolas"


def _captureInputLoad(path: Path) -> Mapping[str, Any]:
    """Load a YAML mapping without accepting language-specific objects."""
    if not path.is_file():
        raise CaptureValidationError(f"Input file does not exist: {path}")
    try:
        loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as error:
        raise CaptureValidationError(f"Could not read input file: {error}") from error
    if not isinstance(loaded, dict):
        raise CaptureValidationError("Input file must contain a YAML mapping.")
    return loaded


def _captureRun(args: argparse.Namespace) -> int:
    """Validate, preview, and optionally persist one continuity record."""
    try:
        interactive = args.input is None
        if args.domain is None:
            if not interactive:
                raise CaptureValidationError(
                    "A domain is required with non-interactive --input."
                )
            domain = captureDomainCapture()
        else:
            domain = args.domain
        print(f"Starting {domain} capture")
        clannPath = _captureClannResolve(args.clann, interactive=interactive)
        if interactive:
            label, source, fields = domainCapture(domain)
        else:
            if not args.label or not args.source:
                raise CaptureValidationError(
                    "--label and --source are required with --input."
                )
            fields = _captureInputLoad(args.input)
            label, source = args.label, args.source
        capture = CaptureInput(domain, label, fields, source)
        targetPath, document = capturePrepare(capture, clannPath)
        print(yaml.safe_dump(document, allow_unicode=True, sort_keys=False).rstrip())
        print(f"Target: {targetPath}")
        if not args.confirm:
            if not interactive or not confirmationCapture(
                "Save this capture record?", default=False
            ):
                print("Preview complete; no files were created.")
                return 0
        captureWrite(targetPath, document)
    except CursesCancelled:
        print("Capture cancelled; no files were created.")
        return 130
    except (CaptureValidationError, CaptureWriteError, OSError, ValueError) as error:
        _statusPrint(f"Error: {error}", colour="red")
        return 1
    _statusPrint(f"Capture complete: {targetPath}", colour="green")
    return 0


def _statusPrint(message: str, *, colour: str) -> None:
    """Print a coloured terminal status with a plain redirected fallback."""
    codes = {"green": "1;37;42", "red": "1;37;41"}
    if sys.stdout.isatty():
        print(f"\033[{codes[colour]}m{message}\033[0m")
    else:
        print(message)


def _captureClannResolve(clannPath: Optional[Path], *, interactive: bool) -> Path:
    """Use an explicit Clann, the sole default, or an interactive choice."""
    if clannPath is not None:
        return clannPath
    clannsPath = _dataRootGet() / "clanns"
    if not clannsPath.is_dir():
        raise CaptureValidationError(
            "No Clanns exist yet. Run `eolas clann --create` first."
        )
    candidates = sorted(
        path
        for path in clannsPath.iterdir()
        if path.is_dir() and (path / "clann.yaml").is_file()
    )
    if not candidates:
        raise CaptureValidationError(
            "No Clanns exist yet. Run `eolas clann --create` first."
        )
    if len(candidates) == 1:
        return candidates[0]
    if not interactive:
        raise CaptureValidationError(
            "Several Clanns exist; use --clann with non-interactive input."
        )
    return clannPathCapture(candidates)


def _parserBuild() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="eolas",
        description="Create and maintain private Eolas Clann records.",
    )
    areas = parser.add_subparsers(dest="area", title="functional areas")

    clannParser = areas.add_parser("clann", help="work with a Clann")
    clannActions = clannParser.add_mutually_exclusive_group(required=True)
    clannActions.add_argument(
        "--create",
        action="store_const",
        const="create",
        dest="action",
        help="interactively create a Clann and primary household",
    )
    clannParser.add_argument(
        "-y",
        "--confirm",
        action="store_true",
        help="generate after displaying the summary without asking",
    )

    captureParser = areas.add_parser(
        "capture", help="capture a structured continuity record"
    )
    captureParser.add_argument(
        "domain",
        nargs="?",
        choices=tuple(CAPTURE_PROFILES),
        help="requirement domain (default: choose from a menu)",
    )
    captureParser.add_argument(
        "--clann",
        type=Path,
        help="existing Clann directory (default: discover and choose)",
    )
    captureParser.add_argument(
        "--input",
        type=Path,
        help="YAML file containing domain fields (default: curses entry)",
    )
    captureParser.add_argument("--label", help="safe human label for YAML input")
    captureParser.add_argument(
        "--source", help="where YAML input information came from"
    )
    captureParser.add_argument(
        "-y",
        "--confirm",
        action="store_true",
        help="save the record (default is a safe preview)",
    )

    logParser = areas.add_parser("log", help="inspect Eolas logs")
    logActions = logParser.add_mutually_exclusive_group(required=True)
    logActions.add_argument(
        "--show",
        action="store_const",
        const="show",
        dest="action",
        help="show ~/eolas/eolas.log",
    )

    return parser


def _logShow() -> int:
    logPath = _dataRootGet() / "eolas.log"
    try:
        contents = logPath.read_text(encoding="utf-8")
    except FileNotFoundError:
        _statusPrint(f"No Eolas log file found: {logPath}", colour="red")
        return 1
    except OSError as error:
        _statusPrint(f"Could not read Eolas log file {logPath}: {error}", colour="red")
        return 1

    print(contents, end="" if contents.endswith("\n") or not contents else "\n")
    return 0


def _positiveIntegerAsk(prompt: str) -> int:
    while True:
        answer = input(prompt).strip()
        try:
            value = int(answer)
        except ValueError:
            print("Please enter a positive whole number.")
            continue
        if value > 0:
            return value
        print("Please enter a positive whole number.")


def _primaryAsk(people: Sequence[PersonInput]) -> int:
    print("\nPrimary person or record owner")
    for index, person in enumerate(people, start=1):
        print(f"  {index}. {person.full_name}")
    while True:
        answer = input("Select the primary person by number: ").strip()
        try:
            selected = int(answer)
        except ValueError:
            print("Please enter one of the listed numbers.")
            continue
        if 1 <= selected <= len(people):
            return selected - 1
        print("Please enter one of the listed numbers.")


def _requiredAsk(prompt: str) -> str:
    while True:
        answer = input(prompt).strip()
        if answer:
            return answer
        print("A value is required.")


def _summaryPrint(clann: ClannInput, targetPath: Path) -> None:
    print("\nSummary")
    print(f"  Clann: {clann.name}")
    print(f"  Primary household: {clann.primary_household_name}")
    print(f"  Target: {targetPath}")
    print("  People:")
    for person in clann.people:
        primaryMarker = " (primary)" if person.is_primary else ""
        residence = (
            "resident" if person.lives_in_primary_household else "lives elsewhere"
        )
        ageLabel = "adult" if person.is_adult else "minor"
        print(
            f"    - {person.full_name} [household role: "
            f"{person.household_role}; age: {ageLabel}; "
            f"residence: {residence}]{primaryMarker}"
        )
