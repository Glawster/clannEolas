# Architecture decision records

Architecture decision records (ADRs) preserve important project-shaping choices
and the reasons behind them. Architecture here includes the handbook's content,
information model, privacy boundaries and delivery approach—not only software.

Name records `ADR-<fourDigitNumber>-<shortName>.md`. Each record states its
status, context, decision and consequences and links to affected requirements.
ADRs are append-only historical records: do not rewrite an accepted decision to
make a new choice appear inevitable. Instead, add a new ADR and mark the old
record `superseded`, with links in both directions.

Valid statuses are `proposed`, `accepted`, `deprecated` and `superseded`.

## Keystone ADR

[ADR-0007: Knowledge before documents](ADR-0007-knowledgeBeforeDocuments.md) is
the project's keystone architectural decision. When work is uncertain, begin
with its test:

> **Am I modelling knowledge, or am I modelling a document?**

Document-shaped models usually indicate that the underlying knowledge should be
identified first. Requirements concerned genuinely with presentation remain
valid, but presentation must not become the source of truth.

## Records

- [ADR-0001: Handbook before software](ADR-0001-handbookBeforeSoftware.md)
- [ADR-0002: Offline first](ADR-0002-offlineFirst.md)
- [ADR-0003: Never store passwords](ADR-0003-neverStorePasswords.md)
- [ADR-0004: Public templates and private data](ADR-0004-publicTemplatesPrivateData.md)
- [ADR-0005: Information classification](ADR-0005-informationClassification.md)
- [ADR-0006: One shared domain model, many projections](ADR-0006-sharedDomainModel.md) — superseded by ADR-0007
- [ADR-0007: Knowledge before documents](ADR-0007-knowledgeBeforeDocuments.md) — keystone ADR
