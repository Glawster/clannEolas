# Terminal interface

Eolas provides a full-screen terminal interface built with Textual.

The TUI is the primary interactive application interface. The existing
`eolas` command-line interface remains available for scripted and
non-interactive workflows.

## Launch

Install the project in the active development environment:

```bash
python -m pip install -e .
```

Launch the terminal interface with:

```bash
eolas-tui
```

or:

```bash
python -m eolas.tui
```

## Interaction model

The interface uses persistent left-hand navigation and a central workspace.

Number keys provide direct navigation between major areas. Tab and arrow-key
navigation remain available through Textual, and mouse interaction is optional.

The overview presents a small number of summary cards, a full-width overall
readiness indicator, and a table of areas requiring attention.

Sensitive values must be masked or omitted in summary views. A future detail
view may reveal information only when appropriate to the user's explicit
action.

## Architecture

Textual is confined to `eolas/tui/`. The TUI must use the same
application/domain services as the command-line interface and must not shell
out to CLI commands.

The framework decision is recorded in
[ADR-019](../project/adr/019-textualTerminalInterface.md).

REQ-020 remains in progress while shared-service integration, interaction tests
and cross-platform smoke testing are completed.
