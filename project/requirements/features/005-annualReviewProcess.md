# 005: Annual review process

Priority: high  
Owner: project maintainers

## Status

ToDo

## Outcome

As a handbook owner, I need a repeatable annual and event-triggered review so
that trusted readers do not rely on stale information.

## Context

The process must remain short enough for routine use while checking references,
trusted-reader access, backups, follow-up actions and disposal of obsolete
copies. It must work without software or vendor services.

## Scope

- Annual review and significant-life-event triggers.
- Review responsibility, change recording and obsolete-copy disposal.
- Contact, care, legal, financial, home, health, digital, final-wishes and family-knowledge checks.

## Out of scope

- Automatic reminders or software notifications.
- Recording passwords or other secrets during review.

## Acceptance criteria

1. The checklist covers changes in every handbook topic named in Scope.
2. The process includes secure handling of superseded paper and digital copies.
3. A fictional walkthrough can complete the review without software or vendor services.

## Dependencies and decisions

- Requires [001](001-handbookFoundation.md), [002](002-privacyAndSecurityModel.md) and [003](003-handbookContentStructure.md); related to 004 and 006.
- ADRs: [ADR-0002](../../adr/002-offlineFirst.md), [ADR-0003](../../adr/003-neverStorePasswords.md), [ADR-0007](../../adr/007-knowledgeBeforeDocuments.md), [ADR-0008](../../adr/008-handbookAsProjection.md).
- Open question: which life events trigger an immediate review?

## Verification

- Checklist coverage and privacy reviews.
- Fictional scenario walkthrough.

## Traceability

- Implementation: [Annual Review](../../../handbook/11-AnnualReview.md)
- Tests: pending
- Documentation: [domain model](../../../documentation/domainModel.md)
- Pull request: pending
- Agent runs: None

## Change history

- 2026-07-22: created as `HB-005-AnnualReviewProcess.yaml`.
- 2026-07-28: migrated to permanent numeric Markdown path; outcome and evidence retained.
