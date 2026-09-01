# Current increment

## Increment

OMP 0.6 scaffold reconciliation.

## Objective

Bring repository-owned documentation, navigation and test configuration into
conformance with the applied OMP 0.6 scaffold without reverting scaffold or
shared-domain-foundation work.

## Scope

- Replace nested repository-owned `README.md` indexes with folder-derived names.
- Repair internal links after scaffold moves and prompt flattening.
- Keep pytest cache artifacts outside the repository working tree.
- Verify the repository with `manageProject --check` and the complete test suite.

## Acceptance work

- Scaffold findings resolved.
- Existing shared-domain implementation preserved.
- Requirement lifecycle statuses unchanged.

## Verification

- `manageProject --check`: passed with zero failures and zero warnings.
- `pytest`: passed after aligning the repository link test with relocated
  managed OMP documentation.

## Immediate next action

Review and commit the scaffold reconciliation with the shared-domain foundation.
