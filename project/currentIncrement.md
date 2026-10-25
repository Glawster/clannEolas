# Current increment

## Increment

Banking dependency graph and closure readiness.

## Branch

`feature/banking-core`

## Objective

Persist Banking-published continuity dependencies and explain the records
upstream and downstream of an account without crossing a Clann boundary.

## Scope

- `BankingDependency` — a classified, reviewed Banking-published graph edge.
- Persistence and endpoint validation through the shared `RecordStore` port.
- Cycle-safe upstream/downstream account impact.
- Closure readiness that lists all connected dependencies and blocks active
  essential ones.

## Explicit exclusion

Do not implement:

- full transaction history or a ledger;
- Direct Debit or standing-order processing and cancellation workflows;
- bank-statement parsing, OCR or Open Banking;
- payment instruments, banking reports or executor/attorney workflows;
- dependencies owned by another module.

## Expected exit criteria

- Tests prove dependency persistence, endpoint validation, Clann isolation,
  cycle-safe impact traversal and closure blocking for essential dependencies.
- Requirement 009 remains in progress.
- `pytest` passes.
- `manageProject --check` reports zero failures and zero warnings.

## Immediate next action

Implement payment instruments and banking equipment, then add Banking Summary
and dependency report projections.
