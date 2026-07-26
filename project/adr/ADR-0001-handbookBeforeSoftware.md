# ADR-0001: Handbook before software

- Status: accepted
- Date: 2026-07-22
- Related requirements: HB-001, HB-003

## Context

The project's purpose is to help a family find and understand practical
information during difficult circumstances. A future application might improve
some workflows, but it could also introduce dependencies, delay useful content
or make the handbook inaccessible when the software is unavailable.

## Decision

The human-readable handbook is the primary product. Content, structure, safety
guidance and print use will be established before any web or desktop
application is considered. The handbook must remain independently useful if no
application is ever built.

## Consequences

- Requirements and content work take priority over application development.
- No planned software capability may be presented as current functionality.
- Future software must consume or produce open, human-readable information and
  cannot become the only practical way to use the handbook.
- Some automation and richer interaction are deferred.
