# Change log

## 0.2a1

- Added recoverable removal and restoration of incomplete Clann directories.
  Removed directories are moved to a private wastebasket, `--restore` lists
  available directories for selection, and `-y` bypasses the final confirmation
  for both actions.

## 0.1a1

- First alpha build identifier for the working Eolas command-line prototype.

## 2026-10-23

- Added persistent Banking-owned continuity dependencies with validated,
  Clann-scoped endpoints, cycle-safe account impact and closure readiness that
  lists connected dependencies and blocks active essential ones.
- Guided the required Banking capture fields with plain-language explanations,
  fictional examples, category/status menus and immediate date-format feedback.
- Added read-only `eolas clann --list` and `eolas clann --status` commands for
  discovering usable Clanns and identifying incomplete directories.
- Rejected abbreviated CLI options and validate an explicit `--clann` path
  before opening the private capture form.
- Normalised all-lowercase/all-uppercase user input by field purpose while
  preserving mixed-case text, semantic availability states and identifiers.
- Added conservative `eolas clann --repair` recovery for partial
  manifest-less Clann folders that contain no files to overwrite.
- Allow `eolas clann --repair` to select the sole incomplete directory and
  direct capture to that recovery path when no usable Clann exists.
- Documented reusable software-workflow principles for meaningful discovery,
  guided recovery, contextual input help, conservative normalisation and
  preview-before-change behavior.

## 2026-09-10

- Implemented Banking Core: `FinancialInstitution`, `BankingRelationship`,
  `AccountParty`, versioned continuity roles, typed identifiers,
  `BalanceObservation`, authority links, and persistence through the shared
  `RecordStore` port.
- Adapted `eolas capture banking` so CLI/curses input creates typed Banking
  records rather than a loose capture dictionary.
- New Clann bootstrap allocates opaque `rec_` person and household IDs and
  persists `Person` aggregates to the shared store. Banking capture reuses
  existing people and institutions by stable reference or unique exact name.
- Added `Obligation`, `PaymentArrangement`, `MoneyMovement` and
  `TransactionObservation`, keeping the bill, the payment instruction, the
  expected flow and statement evidence as separate records.
- Requirement 009 remains in progress; statement import, payment processing
  and banking projections are not included.

## 2026-09-01

- Accepted the Phase 0 identity, persistence, party, authority, evidence and
  module-boundary ADRs.
- Implemented the Phase 1 shared knowledge kernel, dependency graph and
  versioned local persistence boundary.
- Refactored generic capture into a typed input adapter using shared secret and
  availability-state validation.
- Added the fictional Phase 1 cross-domain conformance scenario and tests.
