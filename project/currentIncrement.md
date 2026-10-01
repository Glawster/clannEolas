# Current increment

## Increment

REQ-020 — Interactive cross-platform terminal interface.

## Branch

`feature/020-interactive-terminal-interface`

## Objective

Turn the reviewed Textual shell into the main Eolas terminal interface while
preserving the scriptable CLI and keeping domain behaviour outside the UI.

## Scope

- Maintain the approved left-navigation and central-workspace interaction model.
- Use the Eolas/FMSAT visual language through externalised Textual styling.
- Keep Textual code beneath `eolas/tui/`.
- Connect representative views and forms to shared application/domain services.
- Preserve masked/omitted sensitive values in summary contexts.
- Add interaction tests for navigation, validation, confirmations and resizing.
- Preserve existing CLI behaviour.

## Explicit exclusion

- Desktop, browser and mobile interfaces.
- Business rules implemented in Textual views.
- Completing unfinished Banking or other domain functionality solely to fill
  TUI screens.

## Expected exit criteria

- `eolas-tui` launches the production TUI shell.
- Representative TUI workflows use shared services rather than CLI subprocesses.
- Existing CLI workflows continue to pass regression tests.
- Responsive layout, keyboard navigation, validation and confirmation have
  automated interaction evidence.
- Sensitive-data presentation has been reviewed.
- Linux, macOS and Windows smoke tests are recorded.
- `pytest`, repository linting and `manageProject --check` pass.

## Immediate next action

Replace remaining temporary display data with shared-service-backed Clann and
domain projections, then add Textual interaction tests.
