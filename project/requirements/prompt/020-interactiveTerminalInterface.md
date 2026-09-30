# REQ-020: Interactive cross-platform terminal interface

## Role

Refine, design and implement the interactive terminal interface defined by
`project/requirements/features/020-interactiveTerminalInterface.md`.

## Requirement

The authoritative requirement is:

- `project/requirements/features/020-interactiveTerminalInterface.md`

Do not redefine the product outcome in this prompt. If implementation work
reveals that the agreed outcome or acceptance criteria must change, update the
requirement through the normal requirements process before continuing.

## Objective

Deliver a maintainable full-screen terminal frontend for Clann Eolas that uses
the same application/domain services as the scriptable CLI and operates from a
common codebase on Linux, macOS and Windows.

## Constraints

- Read and follow `.github/agent-instructions.md`,
  `.github/additional-instructions.md`,
  `documentation/requirementsManagement.md`,
  `documentation/repositoryLayout.md` and
  `documentation/testingProcess.md`.
- Do not move business logic into the TUI.
- Do not implement TUI actions by invoking Clann Eolas CLI commands as
  subprocesses.
- Preserve existing CLI behaviour unless a separately agreed requirement says
  otherwise.
- Keep the TUI framework isolated to presentation modules.
- Prefer reusable views/widgets and externalised styling over large monolithic
  UI files.
- Use the established FMSAT visual language as the default theme.
- Keep sensitive information out of routine status, log and summary output.
- Preserve safe-by-default behaviour for data-changing actions.

## Architecture work

Before implementation, confirm whether the framework choice is consequential
enough to require an ADR. Textual is the current candidate because the
requirement needs cross-platform full-screen terminal layout, keyboard
interaction, forms/tables, live progress, responsive resizing and externalised
styling, but the requirement is framework-neutral.

The resulting dependency flow should remain conceptually:

```text
CLI ─┐
     ├──> application/domain services ──> persistence
TUI ─┘
```

The TUI must not depend on CLI parsing or console-output functions to access
domain behaviour.

## Implementation scope

Implement only the interface capabilities needed to satisfy the acceptance
criteria with representative existing Clann Eolas workflows. Do not broaden
domain functionality merely to populate screens.

Provide:

- application launch and exit behaviour;
- primary navigation;
- representative list/detail views;
- representative create/edit form handling;
- validation and safe confirmation behaviour;
- live progress/status integration;
- responsive terminal resizing;
- reusable TUI components and externalised theme/style resources;
- cross-platform packaging/dependency updates where required; and
- documentation for launching and using the TUI.

## Verification

Run the repository-standard test suite and add focused tests for:

- TUI launch;
- keyboard navigation;
- form validation;
- service-layer integration;
- confirmation handling;
- representative long-running progress updates;
- resizing/layout behaviour where the framework supports deterministic tests;
- sensitive-data masking in summary/status contexts; and
- regression of existing CLI behaviour.

Also perform documented smoke tests on Linux, macOS and Windows modern terminal
environments before marking the requirement complete.

## Handoff

Report:

- files changed;
- architecture/ADR decisions;
- acceptance criteria satisfied and any still pending;
- automated test commands and results;
- manual platform verification performed;
- known terminal/framework limitations; and
- any follow-on requirement that should be captured separately.
