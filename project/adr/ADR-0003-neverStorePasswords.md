# ADR-0003: Never store passwords

- Status: accepted
- Date: 2026-07-22
- Related requirements: HB-002, HB-004, HB-005

## Context

A handbook containing passwords, PINs or recovery codes would become a
high-value credential store. Copies may be printed, backed up, shared with
trusted people or left accessible during an emergency, increasing the impact
of loss or unauthorised access.

## Decision

Ordinary handbook content will never store or request passwords, PINs or
recovery codes. It may identify the existence of an appropriate credential
management or access process and safely reference where instructions can be
found.

## Consequences

- Templates and examples must not contain fields for reusable secrets.
- Digital-life guidance must direct people toward a separate, suitable access
  arrangement without prescribing one vendor.
- Reviews check that access instructions remain valid, not that credentials
  have been copied into the handbook.
- A trusted reader may need a separate authorised process to gain access.
