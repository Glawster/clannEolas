"""Tests for Banking-published continuity dependency storage and impact."""

from datetime import date
from pathlib import Path

import pytest

from eolas.banking.dependencies import DEPENDENCY_AGGREGATE, BankingDependency
from eolas.banking.payments import MoneyMovement, MovementDirection
from eolas.banking.service import BankingService
from eolas.domain.graph import ContinuityDependency
from eolas.domain.values import (
    Classification,
    DomainValidationError,
    Fact,
    FactState,
    RecordIdentity,
    ReviewState,
    Schedule,
)
from tests.test_bankingPayments import CLANN, _account, _provenance, _review, _service


def _dependency(
    source, target, dependency_type: str, explanation: str, *, essentiality="essential"
) -> BankingDependency:
    return BankingDependency(
        RecordIdentity.identityCreate(CLANN, DEPENDENCY_AGGREGATE, "banking"),
        ContinuityDependency(
            source,
            target,
            dependency_type,
            _provenance(),
            explanation,
        ),
        Classification.CONFIDENTIAL,
        essentiality,
        _review(),
    )


def testDependencyPersistsAndExplainsAccountImpact(tmp_path: Path) -> None:
    service = _service(tmp_path)
    _organisation, _institution, account = _account(service)
    salary = service.movementCreate(
        MoneyMovement(
            RecordIdentity.identityCreate(CLANN, "moneyMovement", "banking"),
            MovementDirection.INFLOW,
            "Fictional salary",
            account.identity.referenceCreate(),
            Classification.CONFIDENTIAL,
            _provenance(),
            _review(),
            Schedule("monthly", Fact(FactState.UNKNOWN), "variable"),
        )
    )
    electricity = service.movementCreate(
        MoneyMovement(
            RecordIdentity.identityCreate(CLANN, "moneyMovement", "banking"),
            MovementDirection.OUTFLOW,
            "Fictional electricity payment",
            account.identity.referenceCreate(),
            Classification.CONFIDENTIAL,
            _provenance(),
            _review(),
            Schedule("monthly", Fact(FactState.UNKNOWN), "variable"),
        )
    )
    incoming = service.dependencyCreate(
        _dependency(
            salary.identity.referenceCreate(),
            account.identity.referenceCreate(),
            "paidInto",
            "Fictional salary is paid into the operating account.",
        )
    )
    outgoing = service.dependencyCreate(
        _dependency(
            account.identity.referenceCreate(),
            electricity.identity.referenceCreate(),
            "funds",
            "The operating account funds the electricity payment.",
        )
    )

    impact = service.dependencyImpact(account.identity.referenceCreate())

    assert impact.upstream[0].edges == (incoming.dependency,)
    assert impact.downstream[0].edges == (outgoing.dependency,)
    assert service.dependencyGet(outgoing.identity) == outgoing


def testClosureIsBlockedByEssentialDependenciesAndCyclesTerminate(tmp_path: Path) -> None:
    service = _service(tmp_path)
    _organisation, _institution, account = _account(service)
    movement = service.movementCreate(
        MoneyMovement(
            RecordIdentity.identityCreate(CLANN, "moneyMovement", "banking"),
            MovementDirection.OUTFLOW,
            "Fictional care cost",
            account.identity.referenceCreate(),
            Classification.CONFIDENTIAL,
            _provenance(),
            _review(),
            Schedule("monthly", Fact(FactState.UNKNOWN), "variable"),
        )
    )
    service.dependencyCreate(
        _dependency(
            account.identity.referenceCreate(),
            movement.identity.referenceCreate(),
            "funds",
            "The account funds fictional care costs.",
        )
    )
    service.dependencyCreate(
        _dependency(
            movement.identity.referenceCreate(),
            account.identity.referenceCreate(),
            "reconcilesWith",
            "The payment is reconciled to the operating account.",
            essentiality="important",
        )
    )

    readiness = service.relationshipClosureReadiness(account.identity.referenceCreate())
    impact = service.dependencyImpact(account.identity.referenceCreate())

    assert not readiness.ready
    assert len(readiness.dependencies) == 2
    assert len(readiness.blocking_dependencies) == 1
    assert len(impact.downstream) == 2


def testDependencyRejectsMissingAndCrossClannEndpoints(tmp_path: Path) -> None:
    service = _service(tmp_path)
    _organisation, _institution, account = _account(service)
    missing = RecordIdentity.identityCreate(
        CLANN, "moneyMovement", "banking"
    ).referenceCreate()
    with pytest.raises(DomainValidationError, match="persisted canonical endpoints"):
        service.dependencyCreate(
            _dependency(
                account.identity.referenceCreate(),
                missing,
                "funds",
                "Invalid missing target.",
            )
        )

    foreign = RecordIdentity.identityCreate(
        "another-clann", "moneyMovement", "banking"
    ).referenceCreate()
    with pytest.raises(DomainValidationError, match="Cross-Clann"):
        _dependency(
            account.identity.referenceCreate(),
            foreign,
            "funds",
            "Invalid cross-Clann target.",
        )
