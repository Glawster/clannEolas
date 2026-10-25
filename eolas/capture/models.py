"""Validation profiles for CLI-based continuity capture."""

from dataclasses import dataclass
from datetime import date
from typing import Any, Dict, Mapping, Tuple

from eolas.domain.security import secretsValidate
from eolas.domain.values import Classification, DomainValidationError
from eolas.inputNormalise import (
    codeNormalise,
    controlledValueNormalise,
    sentenceNormalise,
    titleNormalise,
)


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

ALLOWED_CLASSIFICATIONS = {item.value for item in Classification}
CONTROLLED_VALUES = {
    "classification": {item.value.casefold(): item.value for item in Classification},
    "status": {
        "active": "active",
        "inactive": "inactive",
        "dormant": "dormant",
        "restricted": "restricted",
        "closurepending": "closurePending",
        "closed": "closed",
        "unknown": "unknown",
    },
    "essentiality": {
        "essential": "essential",
        "important": "important",
        "nonessential": "nonEssential",
        "unknown": "unknown",
    },
}
TITLE_FIELDS = {
    "institution",
    "productName",
    "owners",
    "issuer",
    "borrowers",
    "provider",
    "memberRef",
    "insurer",
    "administrator",
    "policyholders",
    "authority",
    "supplier",
    "accountHolders",
    "beneficiaries",
}
SENTENCE_FIELDS = {"purpose", "service", "obligationPurpose", "paymentPurpose"}
CODE_FIELDS = {"currency", "transactionCurrency", "balanceCurrency"}
FACT_STATE_VALUES = {
    "unknown": "unknown",
    "notapplicable": "notApplicable",
}


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

        try:
            secretsValidate(self.fields)
        except DomainValidationError as error:
            raise CaptureValidationError(str(error)) from error


def _valueMissing(value: Any) -> bool:
    return value is None or value == "" or value == [] or value == {}


def captureNormalise(capture: CaptureInput) -> CaptureInput:
    """Apply field-aware casing while preserving mixed case and identifiers."""
    fields = {
        field: _fieldNormalise(field, value) for field, value in capture.fields.items()
    }
    return CaptureInput(
        capture.domain,
        titleNormalise(capture.label),
        fields,
        sentenceNormalise(capture.source),
    )


def _fieldNormalise(field: str, value: Any) -> Any:
    if isinstance(value, str) and value.strip().casefold() in FACT_STATE_VALUES:
        return FACT_STATE_VALUES[value.strip().casefold()]
    if field in CONTROLLED_VALUES:
        return controlledValueNormalise(value, CONTROLLED_VALUES[field])
    if not isinstance(value, str):
        return value
    if field in TITLE_FIELDS:
        return titleNormalise(value)
    if field in SENTENCE_FIELDS:
        return sentenceNormalise(value)
    if field in CODE_FIELDS:
        return codeNormalise(value)
    return value.strip()
