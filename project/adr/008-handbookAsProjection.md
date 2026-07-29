# 008: Handbook as a projection of household knowledge

- Status: accepted
- Date: 2026-07-22
- Related requirements: [001](../requirements/features/001-handbookFoundation.md), [003](../requirements/features/003-handbookContentStructure.md), [005](../requirements/features/005-annualReviewProcess.md), [006](../requirements/features/006-gettingStartedGuide.md)

## Context

007 establishes that clanneolas.com models knowledge rather than
documents. A further distinction is needed because the project name and current
repository structure can make the handbook appear to be the complete product
or the source of truth.

The handbook is important, especially because it provides a durable,
human-readable and printable experience. It is not, however, the household
knowledge itself. The same knowledge may support an emergency summary, annual
review checklist, medical information sheet, executor pack or future software
experience.

If the handbook is treated as the underlying model, future interfaces are
likely to copy its chapters, headings and page sequence directly. That would
produce document-shaped data and interfaces rather than experiences designed
for a person's situation.

## Decision

The handbook is a projection of shared household knowledge. It is one of many
possible outputs and is not the project itself or the source of truth.

Design will follow this sequence:

```text
Knowledge → Projection → User Experience
```

It will not assume this sequence:

```text
Document → User Interface
```

A projection selects, orders, groups and explains knowledge for a particular
purpose and audience. A user experience presents that projection through an
appropriate medium, such as Markdown, paper, PDF or future software.

The handbook remains the first and foundational projection. In accordance with
001, it must be useful before software and remain useful without software.
Being foundational does not make its chapter structure the domain model.

## Rationale

People need different views in different circumstances. Someone beginning
their planning needs explanation and manageable steps. Someone responding to an
emergency needs a concise, prioritised summary. An executor may need a view of
roles, documents, contacts and actions relevant to estate administration.

These experiences can draw from the same knowledge without independently
maintaining it. Separating knowledge, projection and experience allows each
view to serve its audience without redefining the underlying concepts.

## Consequences

### Positive

- Handbook chapters can be designed for human understanding without becoming a
  storage schema.
- Future interfaces can be task-oriented rather than copies of document pages.
- Emergency, review, print and software experiences can reuse the same
  knowledge.
- Presentation changes do not require redefining household concepts.
- The handbook remains valuable even as other projections are introduced.

### Negative

- Contributors must distinguish domain concepts, projection rules and
  presentation choices.
- A heading in the handbook does not automatically justify a domain entity or
  software screen.
- Traceability is needed to show which knowledge each projection uses.
- Some apparently simple document changes may reveal a missing or ambiguous
  domain concept that must be resolved first.

## Implications for design

When proposing a handbook or interface feature, contributors should ask:

- Which household knowledge does this experience need?
- What should this projection include, omit, order or summarise?
- Who is the projection for, and in what situation will they use it?
- Does another projection already use the same knowledge?
- Is a proposed screen merely copying a page, or serving a distinct user need?
- Can the experience work without creating or maintaining a duplicate value?

A requirement may legitimately target a particular projection or user
experience. It must still trace to the shared domain concepts and must not make
that presentation the authoritative copy of household knowledge.

## Example

An emergency contact is household knowledge associated with people, roles and
possibly instructions.

- The handbook may present it with explanatory context.
- An emergency summary may show only the most urgent contacts in priority
  order.
- An annual review may ask whether the contact and their role are still valid.
- Future software may provide a focused emergency view.

These are different projections and experiences. They must not become four
independently maintained emergency-contact records.

## Relationship to other ADRs

- [001](001-handbookBeforeSoftware.md) establishes that the handbook
  is delivered before software and remains independently useful.
- [002](002-offlineFirst.md) requires essential projections to work
  offline where practical.
- [006](006-sharedDomainModel.md) is the superseded first record of a
  shared domain model and multiple projections.
- [007](007-knowledgeBeforeDocuments.md) is the keystone decision that
  knowledge, not documents, is modelled.

## Related principles

- P-001: People before paperwork.
- P-002: Help families continue confidently.
- P-003: Explain before asking.
- P-005: Technology should disappear.
- P-006: The handbook must remain useful on paper.
- P-009: Open and adaptable.

## Future considerations

This ADR does not define a projection language, rendering system, user
interface framework or storage technology. Those choices require separate
requirements and decisions.

It establishes the relationship that future approaches must preserve:

> **Household knowledge is selected into a projection, and that projection is
> presented as a user experience.**
