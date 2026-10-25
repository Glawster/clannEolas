# 021: Placeholder follow-up tasks

Priority: medium  
Owner: project maintainers

## Status

ToDo

## Outcome

As an Eolas user, I need an explicit follow-up task when I enter `TBC`, `TBA`
or `TBD` as a field value, so that incomplete information is visible and I can
find what still needs to be done.

## Context

People often know that a fact must be confirmed, agreed or determined but
cannot safely complete it during first capture. Treating these markers as
ordinary field values hides the follow-up work, while silently replacing them
with a value such as `unknown` loses the user's intent. Eolas needs a
cross-domain mechanism that preserves the incomplete state and provides one
safe, queryable view of outstanding work.

## Scope

- Recognise a whole, trimmed field value of `TBC`, `TBA` or `TBD`,
  case-insensitively, in interactive and YAML-backed capture flows.
- Create or update a durable follow-up task associated with the affected
  Clann, record and field.
- Record the marker type so the task explains whether the value is to be
  confirmed, agreed or determined.
- Provide `eolas todo --list` to show open follow-up tasks for a selected or
  discovered Clann without requiring users to know the private data layout.
- Show enough safe context to identify the record and field, but do not expose
  the original field value, prohibited secrets or higher-classification
  content in a default list.
- Resolve the associated follow-up task when the field is later replaced by a
  non-placeholder value.
- Keep task creation, update and resolution idempotent so repeated previews,
  retries or imports do not create duplicate tasks.

## Out of scope

- Automatically guessing or supplying the missing field value.
- Treating `TBC`, `TBA` or `TBD` within a longer free-text sentence as a task
  marker.
- Creating tasks from the existing explicit availability states such as
  `unknown` or `notApplicable`.
- Reminder scheduling, notifications, delegated assignment, due dates or
  external task-manager integration.
- Exposing private field values through CLI output, logs or diagnostics.

## Acceptance criteria

1. Given a supported interactive capture field, when the user enters `tbc`,
   `tba` or `tbd` as the complete field value, then Eolas preserves the
   placeholder semantics and creates exactly one open task linked to that
   record and field.
2. Given a YAML-backed capture containing a case variant of a whole-field
   placeholder, when the capture is saved, then the same task is created
   without depending on the interactive UI.
3. Given a field value containing `TBC`, `TBA` or `TBD` as part of a longer
   sentence or identifier, when it is saved, then Eolas does not create a
   placeholder task.
4. Given open placeholder tasks for one Clann, when the user runs
   `eolas todo --list`, then Eolas lists each outstanding record/field and
   marker purpose without requiring a filesystem path or revealing the field
   value.
5. Given a field with an open placeholder task, when the field is updated to a
   non-placeholder value, then its associated task is resolved and no longer
   appears in the default open-task list.
6. Given repeated preview, save or retry operations for the same
   record/field/placeholder, when tasks are inspected, then no duplicate open
   task exists.
7. Given a task-list failure, invalid record reference or inaccessible Clann,
   when the query is run, then Eolas reports a clear error and does not claim
   that incomplete work was resolved.

## Dependencies and decisions

- Depends on the shared Clann record store and capture pipeline introduced by
  requirements 009–018.
- Related to [002 — Privacy and security model](002-privacyAndSecurityModel.md)
  because default task output must not disclose private values.
- Architecture decision: pending. The task aggregate, its lifecycle and its
  projection must be designed before implementation.

## Verification

- Unit tests for exact marker recognition, case handling and non-marker text.
- Integration tests for interactive and YAML-backed capture task creation,
  idempotency and resolution.
- CLI tests for `eolas todo --list`, Clann discovery, safe output and error
  behaviour.
- Privacy review that verifies task lists, logs and errors contain no captured
  field value or prohibited secret.

## Traceability

- Implementation: pending
- Tests: pending
- Documentation: pending
- Pull request: pending
- Agent runs: None

## Change history

- 2026-10-23: created — user requested that `TBC`, `TBA` and `TBD` field
  markers become queryable follow-up tasks.
