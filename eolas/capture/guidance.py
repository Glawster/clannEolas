"""Plain-language field guidance shared by Eolas capture interfaces."""

from dataclasses import dataclass
from typing import Mapping, Tuple


@dataclass(frozen=True)
class FieldGuidance:
    """Explain a capture field without changing its canonical value."""

    label: str
    purpose: str
    example: str

    def promptLines(self) -> Tuple[str, ...]:
        """Return concise form instructions in their display order."""
        return (self.label, self.purpose, f"Example: {self.example}")


BANKING_FIELD_GUIDANCE: Mapping[str, FieldGuidance] = {
    "institution": FieldGuidance(
        "Financial institution",
        "The bank, building society, credit union or card issuer.",
        "Fictional Northbridge Mutual",
    ),
    "accountCategory": FieldGuidance(
        "Account category",
        "Choose the kind of Banking relationship, not the product name.",
        "Current account",
    ),
    "productName": FieldGuidance(
        "Product name",
        "The provider's product label; write unknown if it is not available.",
        "Everyday Current",
    ),
    "purpose": FieldGuidance(
        "Continuity purpose",
        "How this relationship supports the household; do not enter access details.",
        "Household bills and salary",
    ),
    "owners": FieldGuidance(
        "Legal account holders",
        "Use Clann names separated by commas; an unknown name is recorded as a contact.",
        "Alex Example, Morgan Example",
    ),
    "status": FieldGuidance(
        "Account status",
        "Its operational state today, not whether a person is authorised to act.",
        "Active",
    ),
    "classification": FieldGuidance(
        "Information classification",
        "Choose the minimum safe handling level for this relationship.",
        "Confidential",
    ),
    "lastReviewed": FieldGuidance(
        "Last reviewed date",
        "When this information was last checked. Use ISO YYYY-MM-DD.",
        "2026-10-23",
    ),
}


def fieldGuidanceGet(domain: str, field: str) -> FieldGuidance | None:
    """Return domain-specific plain-language guidance when it is available."""
    if domain == "banking":
        return BANKING_FIELD_GUIDANCE.get(field)
    return None
