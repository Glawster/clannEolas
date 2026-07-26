"""Command-line interface for Eolas."""

import argparse
from pathlib import Path
from typing import List, Optional, Sequence

from eolas.clann.models import ClannInput, ClannValidationError, PersonInput
from eolas.clann.service import ClannCreationError, clannCreate
from eolas.clann.slugs import slugCreate

ROLE_SUGGESTIONS = "householder, partner, family, carer, lodger, other"


def cliRun(arguments: Optional[Sequence[str]] = None) -> int:
    """Parse and run an Eolas command."""

    parser = _parserBuild()
    args = parser.parse_args(arguments)
    if args.area == "clann" and args.action == "create":
        return _clannAsk(confirm=args.confirm)
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
    print("Eolas Clann setup")
    print("Generated records contain sensitive personal-data placeholders.")
    print("Do not commit live Clann data to a public repository.\n")

    try:
        name = _requiredAsk("What should this Clann be called? ")
        householdName = _requiredAsk(
            "What is the primary household called? "
        )
        outputDirectory = _outputDirectoryAsk()
        residentCount = _positiveIntegerAsk(
            "How many people currently live there? "
        )
        people = _peopleAsk(residentCount, resident=True)
        while _confirmationAsk(
            "Are there other Clann people to add who live elsewhere?",
            default=False,
        ):
            people.extend(_peopleAsk(1, resident=False))
        primaryIndex = _primaryAsk(people)
        clann = ClannInput(
            name=name,
            primary_household_name=householdName,
            people=[
                PersonInput(
                    full_name=person.full_name,
                    preferred_name=person.preferred_name,
                    household_role=person.household_role,
                    is_adult=person.is_adult,
                    is_primary=index == primaryIndex,
                    lives_in_primary_household=(
                        person.lives_in_primary_household
                    ),
                )
                for index, person in enumerate(people)
            ],
        )
        clann.clannValidate()
        targetPath = outputDirectory / "clanns" / slugCreate(clann.name)
        _summaryPrint(clann, targetPath)
        if not confirm and not _confirmationAsk(
            "Generate these files?", default=True
        ):
            print("Clann setup cancelled; no files were created.")
            return 0
        createdPath = clannCreate(clann, outputDirectory)
    except (EOFError, KeyboardInterrupt):
        print("\nClann setup cancelled; no files were created.")
        return 130
    except (ClannCreationError, ClannValidationError, OSError, ValueError) as error:
        print(f"Error: {error}")
        return 1

    residentCount = sum(
        person.lives_in_primary_household for person in clann.people
    )
    print(f"\nClann created: {createdPath}")
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
        isAdult = _confirmationAsk(
            "  Is this person legally an adult?", default=True
        )
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


def _outputDirectoryAsk() -> Path:
    defaultPath = Path.cwd() / "data"
    answer = input(f"Eolas data directory [{defaultPath}]: ").strip()
    return Path(answer).expanduser().resolve() if answer else defaultPath


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

    logParser = areas.add_parser("log", help="inspect Eolas logs")
    logActions = logParser.add_mutually_exclusive_group(required=True)
    logActions.add_argument(
        "--show",
        action="store_const",
        const="show",
        dest="action",
        help="show data/eolas.log",
    )

    return parser


def _logShow() -> int:
    logPath = Path.cwd() / "data" / "eolas.log"
    try:
        contents = logPath.read_text(encoding="utf-8")
    except FileNotFoundError:
        print(f"No Eolas log file found: {logPath}")
        return 1
    except OSError as error:
        print(f"Could not read Eolas log file {logPath}: {error}")
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
            "resident"
            if person.lives_in_primary_household
            else "lives elsewhere"
        )
        ageLabel = "adult" if person.is_adult else "minor"
        print(
            f"    - {person.full_name} [household role: "
            f"{person.household_role}; age: {ageLabel}; "
            f"residence: {residence}]{primaryMarker}"
        )
