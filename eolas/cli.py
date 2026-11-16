"""Command-line interface for Eolas."""

import argparse
import sys
from pathlib import Path
from typing import Any, List, Mapping, Optional, Sequence

import yaml

from eolas.capture.models import CAPTURE_PROFILES, CaptureInput, CaptureValidationError
from eolas.capture.service import CaptureWriteError, capturePrepare, captureWrite
from eolas.clann.models import ClannInput, ClannValidationError, PersonInput
from eolas.clann.service import (
    ClannCreationError,
    ClannRepairError,
    clannCreate,
    clannRemoveIncomplete,
    clannRepair,
    clannRestoreIncomplete,
)
from eolas.clann.slugs import slugCreate
from eolas.clann.status import clannsInspect, clannsRemoved
from eolas.paths import dataRootGet
from eolas.version import VERSION
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
    """Run the Eolas application or dispatch an explicit CLI command."""

    arguments = sys.argv[1:]
    if not arguments:
        from eolas.tui.app import tuiRun

        return tuiRun()
    return cliRun(arguments)


def cliRun(arguments: Optional[Sequence[str]] = None) -> int:
    """Parse and run an Eolas command."""

    parser = _parserBuild()
    args = parser.parse_args(arguments)
    if args.area == "clann" and args.action == "create":
        return _clannAsk(confirm=args.confirm)
    if args.area == "clann" and args.action == "list":
        return _clannsList()
    if args.area == "clann" and args.action == "status":
        return _clannsStatus()
    if args.area == "clann" and args.remove is not None:
        return _clannRemoveAsk(args.remove, confirm=args.confirm)
    if args.area == "clann" and args.restore is not None:
        return _clannRestoreAsk(args.restore, confirm=args.confirm)
    if args.area == "clann" and args.repair is not None:
        return _clannRepairAsk(args.repair, confirm=args.confirm)
    if args.area == "capture":
        return _captureRun(args)
    if args.area == "log" and args.action == "show":
        return _logShow()
    if args.area == "tui":
        from eolas.tui.app import tuiRun

        return tuiRun()
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
        outputDirectory = dataRootGet()
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
    _statusPrint(f"\nClann created: {createdPath.name}", colour="green")
    print(f"People created: {len(clann.people)}")
    print(f"Primary household residents: {residentCount}")
    return 0


def _clannRepairAsk(targetPath: str, *, confirm: bool) -> int:
    """Capture missing bootstrap facts and complete one partial Clann directory."""
    try:
        targetPath = _repairTargetResolve(targetPath)
        print(f"Checking {targetPath.name} for missing Clann data.")
        print("No readable bootstrap records were found in this directory.")
        print(
            "Enter the Clann, household, and first person details to complete it. "
            "No files change until you confirm the preview; q cancels safely."
        )
        clann = clannCapture()
        clann.clannValidate()
        _summaryPrint(clann, targetPath)
        if not confirm and not confirmationCapture(
            "Write the missing Clann files?", default=True
        ):
            print("Clann repair cancelled; no files were changed.")
            return 0
        repairedPath = clannRepair(clann, targetPath)
    except (CursesCancelled, EOFError, KeyboardInterrupt):
        print("\nClann repair cancelled; no files were changed.")
        return 130
    except (ClannRepairError, ClannValidationError, OSError, ValueError) as error:
        _statusPrint(f"Error: {error}", colour="red")
        return 1

    _statusPrint(f"\nClann repaired: {repairedPath.name}", colour="green")
    return 0


def _clannRemoveAsk(directoryName: str, *, confirm: bool) -> int:
    """Confirm and move one incomplete Clann directory to the wastebasket."""
    try:
        if not confirm and not confirmationCapture(
            f"Remove incomplete Clann directory '{directoryName}'?", default=False
        ):
            print("Clann removal cancelled; no files were changed.")
            return 0
        clannRemoveIncomplete(_dataRootGet(), directoryName)
    except (CursesCancelled, EOFError, KeyboardInterrupt):
        print("\nClann removal cancelled; no files were changed.")
        return 130
    except (ClannRepairError, OSError, ValueError) as error:
        _statusPrint(f"Error: {error}", colour="red")
        return 1

    _statusPrint(
        f"Moved incomplete Clann directory to the wastebasket: {directoryName}",
        colour="green",
    )
    return 0


def _clannRestoreAsk(directoryName: str, *, confirm: bool) -> int:
    """Confirm and restore one incomplete Clann directory from the wastebasket."""
    try:
        directoryName = _restoreTargetResolve(directoryName)
        if not confirm and not confirmationCapture(
            f"Restore incomplete Clann directory '{directoryName}'?", default=False
        ):
            print("Clann restore cancelled; no files were changed.")
            return 0
        clannRestoreIncomplete(_dataRootGet(), directoryName)
    except (CursesCancelled, EOFError, KeyboardInterrupt):
        print("\nClann restore cancelled; no files were changed.")
        return 130
    except (ClannRepairError, OSError, ValueError) as error:
        _statusPrint(f"Error: {error}", colour="red")
        return 1

    _statusPrint(f"Restored incomplete Clann directory: {directoryName}", colour="green")
    return 0


def _restoreTargetResolve(restore: str) -> str:
    """Use an explicit removed directory or choose one from the wastebasket."""
    if restore != "auto":
        return restore
    candidates = clannsRemoved(_dataRootGet())
    if not candidates:
        raise ClannRepairError("No removed incomplete Clann directory was found.")
    print("Removed incomplete Clann directories:")
    for candidate in candidates:
        print(f"- {candidate.name}")
    if len(candidates) == 1:
        return candidates[0].name
    return clannPathCapture(candidates).name


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
    return dataRootGet()


def _clannsList() -> int:
    """List usable Clanns without opening or changing their private records."""
    summaries, issues = clannsInspect(_dataRootGet())
    if not summaries:
        print("No usable Clanns found. Run `eolas clann --create` to create one.")
        if issues:
            print(
                "An incomplete Clann was found. Run `eolas clann --repair` "
                "to complete its missing setup details."
            )
        return 0
    print("Usable Clanns:")
    for summary in summaries:
        print(f"- {summary.name} ({summary.status}; {summary.people_count} people)")
    return 0


def _clannsStatus() -> int:
    """Show usable Clanns plus directories requiring manual attention."""
    dataRoot = _dataRootGet()
    summaries, issues = clannsInspect(dataRoot)
    print(f"Usable Clanns: {len(summaries)}")
    for summary in summaries:
        modified = f"; modified {summary.modified}" if summary.modified else ""
        print(
            f"- {summary.name} ({summary.status}; {summary.people_count} people"
            f"{modified})"
        )
    if issues:
        print("Directories needing attention:")
        for issue in issues:
            print(f"- {issue.path.name}: {issue.reason}; run `eolas clann --repair`")
    return 0


def _repairTargetResolve(repair: str) -> Path:
    """Use an explicit repair folder or the sole incomplete Clann directory."""
    if repair != "auto":
        return Path(repair)
    _summaries, issues = clannsInspect(_dataRootGet())
    if not issues:
        raise ClannRepairError(
            "No incomplete Clann directory was found. "
            "Use `eolas clann --create` to create a new Clann."
        )
    if len(issues) > 1:
        print("Incomplete Clann directories:")
        for issue in issues:
            print(f"- {issue.path.name}: {issue.reason}")
        return clannPathCapture(tuple(issue.path for issue in issues))
    return issues[0].path


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
        resolvedPath = clannPath.expanduser().resolve()
        if not resolvedPath.is_dir() or not (resolvedPath / "clann.yaml").is_file():
            raise CaptureValidationError(
                f"Not an Eolas Clann directory: {resolvedPath}. "
                "Run `eolas clann --status` to inspect available directories."
            )
        return resolvedPath
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
        _summaries, issues = clannsInspect(_dataRootGet())
        if len(issues) == 1:
            raise CaptureValidationError(
                "No usable Clann exists. Repair the incomplete directory first "
                "with `eolas clann --repair`."
            )
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
        allow_abbrev=False,
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {VERSION}",
        help="show the installed Eolas version and exit",
    )
    areas = parser.add_subparsers(dest="area", title="functional areas")

    clannParser = areas.add_parser(
        "clann", help="work with a Clann", allow_abbrev=False
    )
    clannActions = clannParser.add_mutually_exclusive_group(required=True)
    clannActions.add_argument(
        "--create",
        action="store_const",
        const="create",
        dest="action",
        help="interactively create a Clann and primary household",
    )
    clannActions.add_argument(
        "--list",
        action="store_const",
        const="list",
        dest="action",
        help="list usable Clanns",
    )
    clannActions.add_argument(
        "--status",
        action="store_const",
        const="status",
        dest="action",
        help="show usable Clanns and directories needing attention",
    )
    clannActions.add_argument(
        "--repair",
        nargs="?",
        const="auto",
        metavar="DIRECTORY",
        help="repair the sole incomplete Clann, or a specified directory",
    )
    clannActions.add_argument(
        "--remove",
        metavar="DIRECTORY",
        help="move a named incomplete Clann directory to the wastebasket",
    )
    clannActions.add_argument(
        "--restore",
        nargs="?",
        const="auto",
        metavar="DIRECTORY",
        help="list and restore a removed incomplete Clann directory",
    )
    clannParser.add_argument(
        "-y",
        "--confirm",
        action="store_true",
        help="perform the selected action without the final confirmation",
    )

    captureParser = areas.add_parser(
        "capture", help="capture a structured continuity record", allow_abbrev=False
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

    areas.add_parser("tui", help="launch the interactive terminal interface")

    logParser = areas.add_parser("log", help="inspect Eolas logs", allow_abbrev=False)
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
    logPath = dataRootGet() / "eolas.log"
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
    print(f"  Clann folder: {targetPath.name}")
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
