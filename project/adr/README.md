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

## Records

- [ADR-0001: Handbook before software](ADR-0001-handbookBeforeSoftware.md)
- [ADR-0002: Offline first](ADR-0002-offlineFirst.md)
- [ADR-0003: Never store passwords](ADR-0003-neverStorePasswords.md)
- [ADR-0004: Public templates and private data](ADR-0004-publicTemplatesPrivateData.md)
- [ADR-0005: Information classification](ADR-0005-informationClassification.md)
