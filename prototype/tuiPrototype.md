# Eolas TUI prototype

This prototype explores the interaction model described by
[REQ-020](../project/requirements/features/020-interactiveTerminalInterface.md).
It is not the production Eolas interface and does not mark REQ-020 as
implemented.

## What it demonstrates

The prototype uses a full-screen terminal application to demonstrate:

- persistent keyboard-first domain navigation;
- a dashboard with readiness/status information;
- list/table views and drill-down-style explanatory detail;
- masked sensitive values in summary views;
- a structured quick-capture form;
- required-field validation;
- a safe confirmation modal before a hypothetical write;
- visible keyboard shortcuts;
- responsive reflow at narrower terminal widths; and
- the Eolas/FMSAT visual direction using forest green, warm gold and cream.

All records shown by the prototype are fictional. The prototype performs no
persistence and deliberately does not call production domain services.

## Run it

Install the optional prototype dependency from the repository root:

```bash
pip install -e '.[tui-prototype]'
```

Then run:

```bash
python prototype/tuiPrototype.py
```

Useful keys:

```text
1  Overview
2  People
3  Banking
4  Insurance
5  Subscriptions
6  Documents
7  Quick capture
q  Quit
```

The mouse also works in terminals that support it.

## What to evaluate

The prototype is intended to answer interaction questions before production
implementation:

- Does a permanent left-hand navigation area feel right for Eolas?
- Is the overview calm and informative rather than dashboard-heavy?
- Are list/detail views a good fit for financial and household records?
- Is masked summary information sufficient until a user explicitly opens a
  record?
- Does quick capture feel easier than remembering CLI commands?
- Does the FMSAT/Eolas visual language translate well to a terminal?
- Which parts should become reusable production widgets?

Framework selection remains provisional. Using Textual here is a prototype
choice, not yet an ADR or final implementation decision.
