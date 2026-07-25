"""YAML document builders for the initial household structure."""

from datetime import datetime
from typing import Any, Dict, Mapping

from eolas.household.manifest import PERSON_SECTIONS
from eolas.household.models import HouseholdInput, PersonInput
from eolas.household.names import nameParse


def householdDocumentBuild(
    household: HouseholdInput,
    householdId: str,
    personIds: Mapping[int, str],
    timestamp: datetime,
) -> Dict[str, Any]:
    """Build a household index document."""

    primaryIndex = next(
        index for index, member in enumerate(household.members) if member.is_primary
    )
    timestampValue = timestamp.isoformat()
    return {
        "schema": "eolas/household/v1",
        "id": householdId,
        "name": household.name.strip(),
        "primaryPersonRef": personIds[primaryIndex],
        "members": [
            {
                "personRef": personIds[index],
                "role": member.household_role.strip(),
            }
            for index, member in enumerate(household.members)
        ],
        "metadata": {
            "status": "draft",
            "created": timestampValue,
            "modified": timestampValue,
            "lastReviewed": None,
            "nextReview": None,
        },
    }


def identityDocumentBuild(
    person: PersonInput,
    personId: str,
    timestamp: datetime,
) -> Dict[str, Any]:
    """Build the initial Phase 1 identity document for a person."""

    parsedName = nameParse(person.full_name)
    timestampValue = timestamp.isoformat()
    return {
        "schema": PERSON_SECTIONS["identity"]["schema"],
        "personRef": personId,
        "personal": {
            "title": None,
            "firstName": parsedName.first_name,
            "middleNames": parsedName.middle_names,
            "lastName": parsedName.last_name,
            "preferredName": person.preferred_name.strip(),
            "previousNames": [],
            "dateOfBirth": None,
            "placeOfBirth": {
                "townOrCity": None,
                "countyOrRegion": None,
                "country": None,
            },
            "nationality": [],
            "maritalStatus": None,
        },
        "identifiers": {
            "nationalInsuranceNumber": None,
            "nhsNumber": None,
        },
        "documents": {
            "passportRef": None,
            "drivingLicenceRef": None,
            "birthCertificateRef": None,
            "marriageCertificateRef": None,
            "willRef": None,
            "lastingPowerOfAttorneyRefs": [],
        },
        "medicalSummary": {
            "bloodGroup": None,
            "allergiesKnown": None,
        },
        "photograph": {"fileRef": None},
        "notes": None,
        "metadata": {
            "status": "draft",
            "created": timestampValue,
            "modified": timestampValue,
            "lastVerified": None,
            "nextReview": None,
        },
    }


def personDocumentBuild(
    person: PersonInput,
    personId: str,
    householdId: str,
    timestamp: datetime,
) -> Dict[str, Any]:
    """Build a person index document."""

    timestampValue = timestamp.isoformat()
    return {
        "schema": "eolas/person/v1",
        "id": personId,
        "householdRef": householdId,
        "name": {
            "displayName": person.full_name.strip(),
            "preferredName": person.preferred_name.strip(),
        },
        "role": {
            "householdRole": person.household_role.strip(),
            "isAdult": person.is_adult,
            "isPrimary": person.is_primary,
        },
        "sections": {
            sectionName: section["filename"]
            for sectionName, section in PERSON_SECTIONS.items()
        },
        "metadata": {
            "status": "active",
            "created": timestampValue,
            "modified": timestampValue,
            "lastReviewed": None,
            "nextReview": None,
        },
    }
