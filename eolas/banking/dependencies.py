"""Banking-owned continuity dependency edges and account-impact read models."""

from dataclasses import dataclass
from typing import Tuple

from eolas.banking.models import BANKING_MODULE, bankingIdentityValidate
from eolas.domain.graph import ContinuityDependency, DependencyPath
from eolas.domain.security import classificationResolve
from eolas.domain.values import (
    Classification,
    DomainValidationError,
    EvidenceReference,
    Provenance,
    RecordIdentity,
    RecordLifecycle,
    ReviewState,
    clannBoundaryValidate,
)

DEPENDENCY_AGGREGATE = "continuityDependency"
ESSENTIALITY_VALUES = {"essential", "important", "nonEssential", "unknown"}


@dataclass(frozen=True)
class BankingDependency:
    """A classified Banking-published edge between canonical domain records."""

    identity: RecordIdentity
    dependency: ContinuityDependency
    classification: Classification
    essentiality: str
    review: ReviewState
    evidence: Tuple[EvidenceReference, ...] = ()
    lifecycle: RecordLifecycle = RecordLifecycle()

    def __post_init__(self) -> None:
        bankingIdentityValidate(self.identity, DEPENDENCY_AGGREGATE)
        classificationResolve(self.classification)
        if self.essentiality not in ESSENTIALITY_VALUES:
            raise DomainValidationError(
                f"Unsupported dependency essentiality: {self.essentiality}."
            )
        if self.dependency.source.clann_id != self.identity.clann_id:
            raise DomainValidationError(
                "A Banking dependency source must belong to its Clann."
            )
        references = [self.dependency.source, self.dependency.target]
        if self.review.responsible_role.state.value == "known":
            references.append(self.review.responsible_role.value)
        clannBoundaryValidate(
            self.identity.clann_id,
            references=references,
            evidence=self.evidence,
            provenances=(self.dependency.provenance,),
        )


@dataclass(frozen=True)
class AccountImpact:
    """Cycle-safe upstream and downstream paths connected to one account."""

    upstream: Tuple[DependencyPath, ...]
    downstream: Tuple[DependencyPath, ...]


@dataclass(frozen=True)
class AccountClosureReadiness:
    """Explain whether a Banking relationship can be safely closed."""

    ready: bool
    dependencies: Tuple[BankingDependency, ...]
    blocking_dependencies: Tuple[BankingDependency, ...]
