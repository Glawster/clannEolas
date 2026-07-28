# ADR-0004: Public templates and private data

- Status: accepted
- Date: 2026-07-22
- Related requirements: [001](../requirements/features/001-handbookFoundation.md), [002](../requirements/features/002-privacyAndSecurityModel.md), [004](../requirements/features/004-fictionalExampleHousehold.md)

## Context

clanneolas.com is a public, reusable project, while a completed household
handbook may contain sensitive personal, health, financial and family
information. Mixing these concerns risks publishing private data and makes the
public project harder for other families to reuse.

## Decision

Reusable templates, guidance and explicitly fictional examples belong in the
public project. Real household data belongs in a separate private location and
must not be committed to the public repository.

## Consequences

- Public examples must be clearly fictional and contain no usable private
  identifiers or credentials.
- Instructions must make the boundary visible before users enter household
  information.
- Future tooling must keep public source material and private household data
  separate by default.
- The project must document safe storage choices without requiring a particular
  vendor or service.
