# Current increment

## Increment

Banking account closure lifecycle.

## Branch

`feature/banking-closure`

## Objective

Turn closure readiness into a guarded, evidenced closure lifecycle so a Banking
relationship cannot be recorded as closed while essential payments, income or
balance questions remain unresolved (requirement 009, validation rule 9 and
acceptance criteria AC-4.4 and AC-10.1).

## Starting point

Delivered on `feature/banking-core` and carried into this branch:

- `BankingDependency` edges with cycle-safe upstream/downstream account impact.
- `relationshipClosureReadiness()`, which blocks closure only for active
  essential dependency edges.
- `BankingStatus` already includes `closurePending` and `closed`, but
  `relationshipRevise()` accepts any status change without a readiness check.

## Scope

- Extend closure readiness beyond dependency edges to report:
  - active `PaymentArrangement` records funded from the account;
  - active incoming `MoneyMovement` records into the account;
  - a retained-balance question when the latest balance observation is
    non-zero, unknown or undated; and
  - linked products connected through Banking dependency edges.
- Give every readiness item an explainable reason, the record it refers to and
  whether it blocks closure.
- Add closure lifecycle commands with expected-version checks:
  - request closure: `active`, `dormant` or `restricted` to `closurePending`;
  - record closure: `closurePending` to `closed` only when readiness is
    `ready`, recording the closed date, source and evidence reference.
- Prevent `relationshipRevise()` from bypassing the lifecycle by setting
  `closurePending` or `closed` directly.
- Record each closure transition in `RecordStore` history with actor context,
  time and source, and with no prohibited secrets in logs.

## Explicit exclusion

Do not implement:

- payment instruments or cards; readiness must be extended when they exist;
- cancelling, redirecting or transferring payments, income or funds;
- institution notification or any automated closure action;
- bereavement, capacity or other event workflows;
- Banking reports, projections or CLI/TUI closure screens;
- statement import or Open Banking.

## Expected exit criteria

- Tests prove each readiness item type, explainable blocker reasons, both
  closure transitions, rejection of closure while blocked, rejection of a
  direct status bypass, closure history and Clann isolation.
- Requirement 009 remains in progress.
- `pytest` passes.
- `runLinter` reports no findings.
- `manageProject --check` reports zero failures and zero warnings.

## Immediate next action

Extend `relationshipClosureReadiness()` to include funded payment arrangements
and incoming money movements, each with an explainable blocker reason.
