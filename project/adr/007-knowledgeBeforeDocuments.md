# 007: Knowledge before documents

- Status: accepted
- Date: 2026-07-22
- Role: keystone ADR
- Related requirements: [003](../requirements/features/003-handbookContentStructure.md), [004](../requirements/features/004-fictionalExampleHousehold.md), [005](../requirements/features/005-annualReviewProcess.md), [006](../requirements/features/006-gettingStartedGuide.md)
- Supersedes: 006

## Keystone test

When a feature, requirement or design direction is uncertain, ask:

> **Am I modelling knowledge, or am I modelling a document?**

If the answer is “a document”, reconsider the design. First identify the
underlying knowledge, its relationships and its purpose. A document-specific
requirement is appropriate only when it genuinely concerns presentation—for
example readability, page navigation or print layout—and does not redefine the
knowledge itself.

## Context

clanneolas.com is intended to help people organise the practical knowledge
their family may need during emergencies, illness, loss of capacity and
end-of-life administration.

It would be tempting to model the project around documents:

- handbook chapters;
- PDF exports;
- Markdown pages;
- printed worksheets; and
- application screens.

However, these are all **presentations** of information rather than the
information itself.

A printed handbook, a desktop application, a mobile application and an
emergency summary may all contain exactly the same underlying knowledge,
organised differently for different purposes.

If the project models documents first, every new output format risks duplicating
information and introducing inconsistencies.

## Decision

The project shall model **knowledge**, not documents.

Documents are projections of a shared knowledge model.

The domain model represents concepts such as:

- Household;
- Person;
- Contact;
- Property;
- Document;
- Account;
- Asset;
- Instruction;
- Review; and
- Wish.

These concepts exist independently of how they are displayed.

A handbook chapter is a curated view of the knowledge. A printable PDF is
another view. An emergency summary is another view. Future software is another
view.

No presentation format is the source of truth.

## Rationale

Knowledge changes independently of presentation.

For example, a household may update:

- an emergency contact;
- a solicitor;
- an insurance provider;
- a GP; or
- the location of a will.

These changes should occur once within the knowledge model. Every output should
then reflect the updated information.

This avoids duplication, conflicting information and unnecessary maintenance.

## Consequences

### Positive

- A single source of truth.
- Consistent information across outputs.
- Easier maintenance.
- New output formats without redesigning the underlying knowledge.
- Printed and digital outputs remain equally valid.
- Independence from any future software architecture.

### Negative

- The domain model requires more careful design.
- Handbook chapters cannot be designed in complete isolation.
- Contributors must think about concepts rather than pages.
- Additional documentation is needed to explain the relationship between
  knowledge and presentations.

These costs are worthwhile because they improve long-term maintainability.

## Example

The concept **Person** may appear in:

- the family handbook;
- an emergency summary;
- a medical information sheet;
- an executor pack;
- an annual review;
- a desktop application;
- a mobile application; and
- future presentations.

Each presentation selects only the information appropriate for its audience
while referencing the same underlying knowledge.

## Relationship to the domain model

The domain model defines the concepts used by clanneolas.com. The knowledge
model records instances of those concepts. Presentation layers transform that
knowledge into formats suitable for people.

```text
Knowledge
    │
    ▼
Domain Model
    │
    ▼
Structured Household Information
    │
    ├──────────────┐
    │              │
    ▼              ▼
Handbook       Emergency Summary
    │              │
    ├──────────────┤
    ▼              ▼
PDF            Desktop Application
    │              │
    └──────────────┘
           ▼
    Future Presentations
```

## Implications for contributors

When designing new features, contributors should ask:

- Am I modelling knowledge, or am I modelling a document?
- What knowledge is being represented?
- Does this information already exist elsewhere?
- Is this a new concept or another presentation?
- Can this feature reuse an existing concept?
- Should this change be made to the knowledge model instead of a document?

Contributors should avoid coupling requirements to a specific document, PDF
layout or software interface unless the requirement genuinely relates to
presentation.

## Related principles

- P-001: People before paperwork.
- P-004: Privacy by default.
- P-005: Technology should disappear.
- P-006: The handbook must remain useful on paper.
- P-009: Open and adaptable.

The decision also supports the single-source-of-truth approach and
[001: Handbook before software](001-handbookBeforeSoftware.md).

## Related ADRs

- [001: Handbook before software](001-handbookBeforeSoftware.md)
- [002: Offline first](002-offlineFirst.md)
- [003: Never store passwords](003-neverStorePasswords.md)
- [004: Public templates and private data](004-publicTemplatesPrivateData.md)
- [005: Information classification](005-informationClassification.md)
- [006: One shared domain model, many projections](006-sharedDomainModel.md)

## Future considerations

This decision intentionally avoids defining any storage technology, schema,
database or programming language.

Whether knowledge is ultimately stored as Markdown, YAML, JSON, SQLite or
another format is an implementation detail.

The principle established by this ADR remains unchanged:

> **clanneolas.com is a knowledge project. Documents, applications and printed
> handbooks are different ways of presenting that knowledge.**
