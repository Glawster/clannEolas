# 019: Textual terminal interface framework

## Status

accepted

## Context

REQ-020 requires a full-screen terminal interface with keyboard navigation,
tables, forms, modal confirmation, live progress, responsive resizing,
externalised styling and a common Linux, macOS and Windows codebase.

The exploratory interface demonstrated that Textual provides the required
interaction model while keeping the presentation layer separate from Eolas
domain and application services. The visual direction has been accepted as the
foundation for the main Eolas terminal UI.

## Decision

Use Textual as the terminal-interface framework for Eolas.

Production TUI code lives beneath `eolas/tui/`. Textual is a presentation
dependency only: domain, application and persistence code must not import it.

The existing scriptable CLI remains a first-class interface. The TUI must call
shared application/domain services directly rather than invoking CLI commands.

The established Eolas/FMSAT visual language remains the default styling source.

## Consequences

- Textual becomes a normal packaged application dependency.
- The approved TUI shell can evolve directly rather than maintaining a separate
  prototype implementation.
- TUI views, reusable widgets and styling remain presentation concerns.
- Interaction-level tests may use Textual's testing facilities, while domain
  tests remain framework-independent.
- Cross-platform terminal behaviour must still be verified on Linux, macOS and
  Windows before REQ-020 is completed.

## Related requirements

- [REQ-020: Interactive cross-platform terminal interface](../requirements/features/020-interactiveTerminalInterface.md)

## Date

2026-10-01
