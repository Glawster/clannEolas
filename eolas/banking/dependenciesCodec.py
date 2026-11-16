"""Encode and decode Banking-owned continuity dependency aggregates."""

from typing import Any, Mapping

from eolas.banking.codec import BANKING_SCHEMA_VERSION
from eolas.banking.dependencies import (
    DEPENDENCY_AGGREGATE,
    BankingDependency,
)
from eolas.domain.codec import (
    evidenceDecode,
    evidenceEncode,
    lifecycleDecode,
    lifecycleEncode,
    optionalDateDecode,
    optionalDateEncode,
    provenanceDecode,
    provenanceEncode,
    referenceDecode,
    referenceEncode,
    reviewDecode,
    reviewEncode,
    schemaValidate,
)
from eolas.domain.graph import ContinuityDependency
from eolas.domain.storage import StoredRecord
from eolas.domain.values import Classification


def dependencyDecode(record: StoredRecord) -> BankingDependency:
    """Reconstitute a Banking dependency from its stored envelope."""
    schemaValidate(record, DEPENDENCY_AGGREGATE, DEPENDENCY_AGGREGATE)
    payload = record.payload
    dependency = ContinuityDependency(
        referenceDecode(payload["source"]),
        referenceDecode(payload["target"]),
        str(payload["dependencyType"]),
        provenanceDecode(payload["provenance"]),
        str(payload["explanation"]),
        optionalDateDecode(payload.get("effectiveFrom")),
        optionalDateDecode(payload.get("effectiveTo")),
    )
    return BankingDependency(
        record.identity,
        dependency,
        Classification(str(payload["classification"])),
        str(payload["essentiality"]),
        reviewDecode(payload["review"]),
        tuple(evidenceDecode(item) for item in payload.get("evidence", ())),
        lifecycleDecode(payload.get("lifecycle", {})),
    )


def dependencyEncode(dependency: BankingDependency) -> StoredRecord:
    """Encode a Banking dependency without exposing an adapter-specific graph."""
    edge = dependency.dependency
    return StoredRecord(
        dependency.identity,
        DEPENDENCY_AGGREGATE,
        BANKING_SCHEMA_VERSION,
        0,
        {
            "source": referenceEncode(edge.source),
            "target": referenceEncode(edge.target),
            "dependencyType": edge.dependency_type,
            "provenance": provenanceEncode(edge.provenance),
            "explanation": edge.explanation,
            "effectiveFrom": optionalDateEncode(edge.effective_from),
            "effectiveTo": optionalDateEncode(edge.effective_to),
            "classification": dependency.classification.value,
            "essentiality": dependency.essentiality,
            "review": reviewEncode(dependency.review),
            "evidence": [evidenceEncode(item) for item in dependency.evidence],
            "lifecycle": lifecycleEncode(dependency.lifecycle),
        },
    )
