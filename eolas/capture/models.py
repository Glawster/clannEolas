"""Validation profiles for CLI-based continuity capture."""

from dataclasses import dataclass
from datetime import date
from typing import Any, Dict, Mapping, Tuple


class CaptureValidationError(ValueError):
    """Raised when a continuity record is incomplete or unsafe to store."""


@dataclass(frozen=True)
class CaptureProfile:
    """The required fields and schema identity for one continuity domain."""

    schema_name: str
    required_fields: Tuple[str, ...]


CAPTURE_PROFILES: Dict[str, CaptureProfile] = {
    "banking": CaptureProfile(
        "bankAccount",
        (
            "institution",
            "accountCategory",
            "productName",
            "purpose",
            "owners",
            "status",
            "classification",
            "lastReviewed",
        ),
    ),
    "creditCards": CaptureProfile(
        "creditFacility",
        (
            "issuer",
            "facilityType",
            "purpose",
            "borrowers",
            "liabilityBasis",
            "status",
            "maskedReference",
            "currency",
            "paymentAccountRef",
            "repaymentMechanism",
            "statementCycle",
            "classification",
            "lastReviewed",
        ),
    ),
    "mortgages": CaptureProfile(
        "mortgageFacility",
        (
            "lender",
            "mortgageType",
            "purpose",
            "propertyRef",
            "borrowers",
            "liabilityBasis",
            "securityRef",
            "repaymentMethod",
            "status",
            "classification",
            "lastReviewed",
        ),
    ),
    "loans": CaptureProfile(
        "loanFacility",
        (
            "creditor",
            "loanType",
            "purpose",
            "borrowers",
            "liabilityBasis",
            "securityStatus",
            "status",
            "currency",
            "classification",
            "lastReviewed",
        ),
    ),
    "investments": CaptureProfile(
        "investmentRelationship",
        (
            "investmentType",
            "owners",
            "provider",
            "wrapper",
            "jurisdiction",
            "status",
            "currency",
            "classification",
            "lastReviewed",
        ),
    ),
    "pensions": CaptureProfile(
        "pensionArrangement",
        (
            "pensionType",
            "memberRef",
            "provider",
            "status",
            "jurisdiction",
            "maskedReference",
            "classification",
            "lastReviewed",
        ),
    ),
    "insurance": CaptureProfile(
        "insurancePolicy",
        (
            "policyType",
            "purpose",
            "insurer",
            "administrator",
            "policyholders",
            "insuredSubjects",
            "status",
            "jurisdiction",
            "maskedReference",
            "classification",
            "lastReviewed",
        ),
    ),
    "taxation": CaptureProfile(
        "taxRelationship",
        (
            "taxpayerRef",
            "authority",
            "jurisdiction",
            "taxType",
            "filingStatus",
            "period",
            "classification",
            "lastReviewed",
        ),
    ),
    "subscriptions": CaptureProfile(
        "subscription",
        (
            "service",
            "provider",
            "purpose",
            "serviceCategory",
            "ownerRef",
            "beneficiaries",
            "status",
            "paymentRelationship",
            "essentiality",
            "classification",
            "lastReviewed",
        ),
    ),
    "utilities": CaptureProfile(
        "utilityService",
        (
            "utilityType",
            "purpose",
            "premisesRef",
            "supplier",
            "accountHolders",
            "status",
            "paymentRelationship",
            "essentiality",
            "classification",
            "lastReviewed",
        ),
    ),
}

ALLOWED_CLASSIFICATIONS = {
    "public",
    "private",
    "confidential",
    "highlyConfidential",
}

PROHIBITED_KEY_PARTS = (
    "password",
    "passcode",
    "pin",
    "cvv",
    "cvc",
    "securityanswer",
    "recoverycode",
    "seedphrase",
    "privatekey",
    "mfasecret",
    "sessiontoken",
    "accesstoken",
    "onetimecode",
    "signingsecret",
    "gatewaycredential",
)


@dataclass(frozen=True)
class CaptureInput:
    """A validated record supplied to the generic capture workflow."""

    domain: str
    label: str
    fields: Mapping[str, Any]
    source: str

    def captureValidate(self) -> None:
        """Validate profile fields, review metadata, and secret exclusions."""
        if self.domain not in CAPTURE_PROFILES:
            raise CaptureValidationError(f"Unsupported capture domain: {self.domain}")
        if not self.label.strip():
            raise CaptureValidationError("Record label cannot be empty.")
        if not self.source.strip():
            raise CaptureValidationError("Record source cannot be empty.")

        profile = CAPTURE_PROFILES[self.domain]
        missing = [
            field
            for field in profile.required_fields
            if field not in self.fields or _valueMissing(self.fields[field])
        ]
        if missing:
            raise CaptureValidationError(
                "Missing required fields: " + ", ".join(missing)
            )

        classification = self.fields.get("classification")
        if classification not in ALLOWED_CLASSIFICATIONS:
            raise CaptureValidationError(
                "classification must be one of: "
                + ", ".join(sorted(ALLOWED_CLASSIFICATIONS))
            )
        if classification == "highlyConfidential":
            raise CaptureValidationError(
                "Highly Confidential values cannot be stored in capture records."
            )

        reviewValue = self.fields.get("lastReviewed")
        try:
            date.fromisoformat(str(reviewValue))
        except ValueError as error:
            raise CaptureValidationError(
                "lastReviewed must be an ISO date (YYYY-MM-DD)."
            ) from error

        _secretsReject(self.fields)


def _cardNumberLooksComplete(value: str) -> bool:
    digits = "".join(character for character in value if character.isdigit())
    if not 13 <= len(digits) <= 19:
        return False
    if any(character not in "0123456789 -" for character in value):
        return False
    checksum = 0
    parity = len(digits) % 2
    for index, character in enumerate(digits):
        number = int(character)
        if index % 2 == parity:
            number *= 2
            if number > 9:
                number -= 9
        checksum += number
    return checksum % 10 == 0


def _keyNormalise(key: object) -> str:
    return "".join(character for character in str(key).lower() if character.isalnum())


def _secretsReject(value: Any, path: str = "fields") -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            normalised = _keyNormalise(key)
            if any(part in normalised for part in PROHIBITED_KEY_PARTS):
                raise CaptureValidationError(
                    f"Prohibited credential field at {path}.{key}."
                )
            _secretsReject(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _secretsReject(child, f"{path}[{index}]")
    elif isinstance(value, str) and _cardNumberLooksComplete(value):
        raise CaptureValidationError(
            f"Full payment-card number at {path} is prohibited."
        )


def _valueMissing(value: Any) -> bool:
    return value is None or value == "" or value == [] or value == {}
