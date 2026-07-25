"""Typed input models for household creation."""

from dataclasses import dataclass
from typing import List


class HouseholdValidationError(ValueError):
    """Raised when household bootstrap input is invalid."""


@dataclass(frozen=True)
class PersonInput:
    """Information collected for one household member."""

    full_name: str
    preferred_name: str
    household_role: str
    is_adult: bool
    is_primary: bool = False

    def personValidate(self) -> None:
        """Validate this household member."""

        if not self.full_name.strip():
            raise HouseholdValidationError("Person full name cannot be empty.")
        if not self.preferred_name.strip():
            raise HouseholdValidationError("Preferred name cannot be empty.")
        if not self.household_role.strip():
            raise HouseholdValidationError("Household role cannot be empty.")


@dataclass(frozen=True)
class HouseholdInput:
    """Validated information needed to create a household."""

    name: str
    members: List[PersonInput]

    def householdValidate(self) -> None:
        """Validate the household and all of its members."""

        if not self.name.strip():
            raise HouseholdValidationError("Household name cannot be empty.")
        if not self.members:
            raise HouseholdValidationError(
                "A household must contain at least one person."
            )

        for member in self.members:
            member.personValidate()

        primaryCount = sum(member.is_primary for member in self.members)
        if primaryCount != 1:
            raise HouseholdValidationError(
                "A household must have exactly one primary person."
            )
