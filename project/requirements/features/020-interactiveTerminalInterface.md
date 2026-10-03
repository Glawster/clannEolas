# 020: Interactive cross-platform terminal interface

## Status

InProgress

## Outcome

As a Clann Eolas user, I need an interactive terminal interface that presents
the application's existing capabilities through clear navigation, forms,
tables, detail views and live feedback so that I can work with family
information efficiently without learning or composing long CLI command lines.

## Context

Clann Eolas already exposes command-line workflows and is intended to keep
domain knowledge independent of any one presentation layer. A richer terminal
interface would provide a more approachable interactive experience while
preserving the scriptable CLI and avoiding premature commitment to a full
desktop GUI.

The interface should use the same application/domain services as the CLI rather
than invoking CLI commands as an implementation mechanism. This preserves one
source of business behaviour and keeps future desktop, web or mobile frontends
possible.

The target experience is a full-screen terminal application with structured
navigation, selectable lists, detail panels, forms, keyboard shortcuts, status
and progress feedback, modal confirmations where appropriate, and responsive
behaviour when the terminal is resized.

The interface must be usable on Linux, macOS and Windows in supported modern
terminal environments.

## Scope

- Provide a dedicated interactive terminal user interface for Clann Eolas.
- Preserve the existing scriptable CLI as a first-class interface.
- Reuse shared application/domain services for both CLI and TUI operations.
- Keep UI framework dependencies out of core/domain code.
- Provide keyboard-driven navigation between major Clann Eolas domains and
  workflows.
- Provide structured list/table views and drill-down detail views for domain
  records where applicable.
- Provide form-based input for interactive create/edit workflows.
- Provide visible status, validation, progress and completion feedback for
  long-running or multi-step operations.
- Provide confirmation or equivalent safe interaction before operations that
  modify or remove user data.
- Support terminal resizing without corrupting or losing the current
  interaction state.
- Support modern terminals on Linux, macOS and Windows from a common codebase.
- Apply the established FMSAT visual language and colour scheme as the default
  Clann Eolas terminal-interface theme, subject to terminal colour capability
  and accessibility constraints.
- Organise TUI views, reusable widgets and styling as separate presentation
  concerns in accordance with the repository UI organisation rules.
- Ensure sensitive values are not exposed unnecessarily in lists, logs,
  notifications or status output.
- Provide a permanent Help / User Guide area reachable from the main
  navigation so first-time users can understand Eolas, its terminology,
  privacy boundaries and the mechanics of using the TUI without consulting
  source documentation.

## Out of scope

- Replacing or removing the existing command-line interface.
- Implementing business or domain logic inside TUI views or widgets.
- Driving the TUI by shelling out to the existing CLI.
- Building a native desktop GUI, browser UI or mobile application.
- Requiring identical pixel-level appearance across terminal emulators.
- Requiring support for legacy terminal hosts that lack the capabilities
  needed by the chosen TUI framework.
- Expanding domain functionality solely to demonstrate the interface.

## Acceptance criteria

1. Given a supported Clann Eolas installation, when the user launches the
   interactive terminal interface, then a full-screen navigable application
   opens without requiring the user to compose a domain CLI command.
2. Given an existing Clann Eolas domain operation exposed through the TUI, when
   the user performs that operation, then the TUI calls shared application or
   domain services rather than invoking the CLI as a subprocess or duplicating
   the business logic.
3. Given the existing CLI, when REQ-020 is delivered, then existing CLI
   commands remain available for non-interactive and scripted use.
4. Given a user navigating the TUI, when focus moves between available
   controls, views or records, then the active selection is visually clear and
   all primary workflows can be completed with the keyboard.
5. Given a create or edit workflow, when the user enters invalid data, then the
   interface identifies the invalid field or value and prevents invalid state
   from being committed.
6. Given an operation that modifies or removes persisted user data, when the
   user initiates it, then the interface applies the repository's safe-by-
   default behaviour and obtains explicit confirmation where required.
7. Given a long-running operation for which progress can be measured or
   estimated, when it executes, then the TUI remains responsive and displays
   meaningful current activity and progress information rather than appearing
   to have hung.
8. Given a terminal resize during use, when the new dimensions remain above
   the documented minimum supported size, then the interface reflows without
   crashing and preserves the user's current context.
9. Given supported modern terminal environments on Linux, macOS and Windows,
   when the same Clann Eolas TUI package is run, then the core navigation and
   supported workflows operate from the same codebase without platform-
   specific UI rewrites.
10. Given terminal colour support, when the TUI is displayed, then its default
    styling follows the established FMSAT visual language while maintaining
    readable contrast and conveying state through more than colour alone.
11. Given sensitive information in the underlying model, when records are
    shown in summary views, logs, status areas or notifications, then sensitive
    values are masked, omitted or revealed only in an explicit detail context
    appropriate to the user's action.
12. Given automated tests running without an interactive terminal, when the
    TUI-related test suite executes, then core/domain behaviour can still be
    tested independently of the TUI framework and interaction-level TUI tests
    can exercise navigation, validation and service integration without
    requiring manual input.
13. Given a first-time or infrequent user, when they open Help / User Guide
    from the main navigation, then they can find guidance covering Eolas'
    purpose, core terminology, navigation, privacy/safety boundaries and where
    to begin.

## Dependencies and decisions

- Depends on the existing separation between presentation, application/domain
  behaviour and persistence described by the repository development
  guidelines.
- Existing domain requirements remain authoritative for the behaviour the TUI
  exposes.
- Textual is the selected terminal UI framework, recorded in
  [ADR-019](../../adr/019-textualTerminalInterface.md). It provides the required
  cross-platform full-screen layout, keyboard interaction, responsive behaviour,
  reusable widgets, asynchronous/live updates and externalised styling.
- The established FMSAT colour scheme and visual language are the default
  branding source for the interface.

## Verification

- Automated tests demonstrating that domain/application services are usable
  without importing the TUI framework.
- Automated interaction tests covering application launch, navigation,
  selection, forms, validation, confirmations and representative domain
  workflows.
- A test or review demonstrating responsive behaviour across representative
  terminal sizes.
- Manual smoke testing on Linux, macOS and Windows using supported modern
  terminal applications.
- Review of the TUI package structure to confirm that views, reusable widgets
  and styling remain separate from business logic.
- Review of sensitive-data presentation to confirm masking and omission rules
  are applied in summary/status contexts.
- Regression execution of the existing CLI test suite.

## Traceability

- Implementation: `eolas/tui/` production shell established; Create Clann now uses shared `ClannInput`/`PersonInput` validation and `clannCreate()`; remaining domain/service integration continues
- Tests: `tests/test_terminalInterface.py` covers Create Clann navigation, domain validation and persistence integration; execution evidence pending
- Documentation: terminal-interface usage documentation pending
- Pull request: pending
- Agent runs: pending or `None`

## Change history

- 2026-09-30: created — capture the proposed Grok-style interactive terminal
  experience for Clann Eolas while preserving the CLI and shared domain
  architecture.
- 2026-10-01: implementation started — the reviewed Textual shell was promoted
  from prototype status into `eolas/tui/`; Textual was accepted in ADR-019.
- 2026-10-01: Help / User Guide confirmed as a permanent first-class TUI
  navigation area; detailed manual content remains a separate maintained
  documentation concern.
- 2026-10-03: Create Clann migrated into the Textual TUI using the existing
  Clann domain models and atomic creation service; the curses implementation
  remains temporarily for CLI compatibility while migration continues.
