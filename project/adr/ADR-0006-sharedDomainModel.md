# ADR-0006: One shared domain model, many projections

- Status: superseded
- Date: 2026-07-22
- Related requirements: HB-003, HB-004, HB-005
- Superseded by: ADR-0007

## Context

This decision was expanded and superseded by
[ADR-0007: Knowledge before documents](ADR-0007-knowledgeBeforeDocuments.md).
It remains here as a historical record.

The handbook already contains topic-based chapters, and future work may add an
emergency summary, fictional examples, printed layouts or software. If each
output defines household information independently, concepts and values will be
duplicated, terminology will drift and reviews may update one view but not
another.

The project needs a shared understanding of the real-world information it
organises without prematurely choosing a database or application design.

## Decision

familyHandbook will maintain a technology-independent domain model for concepts
such as household, person, property, document, asset, account, contact, wish and
review.

Handbook chapters, summaries, examples, print layouts and future software are
projections of that shared model. A projection may select, order or explain
concepts for a particular situation, but must not create a conflicting domain
definition.

The documented model is conceptual. Candidate information does not commit the
project to software classes, database tables, APIs or a canonical storage
format.

## Consequences

- New content must use shared terms or propose an explicit model change.
- Duplicate information across handbook views should be derived or
  cross-referenced rather than independently maintained.
- Privacy classification and review information apply consistently across
  concepts and projections.
- The model must support paper use and remain understandable without software.
- Storage, identity and synchronisation choices remain separate future
  decisions.
