"""Command-line interface for Eolas."""

import argparse
from pathlib import Path
from typing import List, Optional, Sequence

from eolas.household.models import (
    HouseholdInput,
    HouseholdValidationError,
    PersonInput,
)
from eolas.household.service import HouseholdCreationError, householdCreate
from eolas.household.slugs import slugCreate

ROLE_SUGGESTIONS = "self, spouse, partner, child, parent, relative, other"


def cliRun(arguments: Optional[Sequence[str]] = None) -> int:
    """Parse and run an Eolas command."""

    parser = _parserBuild()
    args = parser.parse_args(arguments)
    if args.command == "ask-household":
        return _householdAsk(confirm=args.confirm)
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


def _householdAsk(*, confirm: bool) -> int:
    print("Eolas household setup")
    print("Generated records contain sensitive personal-data placeholders.")
    print("Do not commit live household data to a public repository.\n")

    try:
        name = _requiredAsk("Household name: ")
        outputDirectory = _outputDirectoryAsk()
        personCount = _positiveIntegerAsk("Number of people in the household: ")
        members = _membersAsk(personCount)
        primaryIndex = _primaryAsk(members)
        household = HouseholdInput(
            name=name,
            members=[
                PersonInput(
                    full_name=member.full_name,
                    preferred_name=member.preferred_name,
                    household_role=member.household_role,
                    is_adult=member.is_adult,
                    is_primary=index == primaryIndex,
                )
                for index, member in enumerate(members)
            ],
        )
        household.householdValidate()
        targetPath = outputDirectory / slugCreate(household.name)
        _summaryPrint(household, targetPath)
        if not confirm and not _confirmationAsk("Generate these files?", default=True):
            print("Household setup cancelled; no files were created.")
            return 0
        createdPath = householdCreate(household, outputDirectory)
    except (EOFError, KeyboardInterrupt):
        print("\nHousehold setup cancelled; no files were created.")
        return 130
    except (
        HouseholdCreationError,
        HouseholdValidationError,
        OSError,
        ValueError,
    ) as error:
        print(f"Error: {error}")
        return 1

    print(f"\nHousehold created: {createdPath}")
    print(f"Members created: {len(household.members)}")
    return 0


def _membersAsk(personCount: int) -> List[PersonInput]:
    members: List[PersonInput] = []
    for index in range(personCount):
        print(f"\nPerson {index + 1} of {personCount}")
        fullName = _requiredAsk("  Full name: ")
        preferredName = _requiredAsk("  Preferred name: ")
        print(f"  Suggested roles: {ROLE_SUGGESTIONS}")
        householdRole = _requiredAsk("  Household role: ")
        isAdult = _confirmationAsk("  Is this person an adult?", default=True)
        members.append(
            PersonInput(
                full_name=fullName,
                preferred_name=preferredName,
                household_role=householdRole,
                is_adult=isAdult,
            )
        )
    return members


def _outputDirectoryAsk() -> Path:
    defaultPath = Path.cwd()
    answer = input(f"Output directory [{defaultPath}]: ").strip()
    return Path(answer).expanduser().resolve() if answer else defaultPath


def _parserBuild() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="eolas",
        description="Create and maintain private Eolas household records.",
    )
    subparsers = parser.add_subparsers(dest="command")
    householdParser = subparsers.add_parser(
        "ask-household",
        help="interactively create an initial household data structure",
    )
    householdParser.add_argument(
        "-y",
        "--confirm",
        action="store_true",
        help="generate after displaying the summary without asking for confirmation",
    )
    return parser


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


def _primaryAsk(members: Sequence[PersonInput]) -> int:
    print("\nPrimary person or record owner")
    for index, member in enumerate(members, start=1):
        print(f"  {index}. {member.full_name}")
    while True:
        answer = input("Select the primary person by number: ").strip()
        try:
            selected = int(answer)
        except ValueError:
            print("Please enter one of the listed numbers.")
            continue
        if 1 <= selected <= len(members):
            return selected - 1
        print("Please enter one of the listed numbers.")


def _requiredAsk(prompt: str) -> str:
    while True:
        answer = input(prompt).strip()
        if answer:
            return answer
        print("A value is required.")


def _summaryPrint(household: HouseholdInput, targetPath: Path) -> None:
    print("\nSummary")
    print(f"  Household: {household.name}")
    print(f"  Target: {targetPath}")
    print("  Members:")
    for member in household.members:
        primaryMarker = " (primary)" if member.is_primary else ""
        adultLabel = "adult" if member.is_adult else "minor"
        print(
            f"    - {member.full_name} [{member.household_role}, "
            f"{adultLabel}]{primaryMarker}"
        )
