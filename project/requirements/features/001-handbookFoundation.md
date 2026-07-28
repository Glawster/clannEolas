# 001: Handbook foundation

Legacy ID: `HB-001`  
Priority: critical  
Owner: project maintainers

## Status

ToDo

## Outcome

As a household member, I need to understand the handbook's purpose, limits and
safe use before adding information, so that I can begin without depending on an
application.

## Context

The handbook needs a trustworthy, application-independent foundation. It must
distinguish reusable public guidance from a private completed handbook and make
clear that it is not legal, medical or financial advice.

## Scope

- Purpose, audience, usage, storage, maintenance and limitations.
- Human-readable source and a practical print-oriented structure.
- Safe first steps and links to privacy guidance.

## Out of scope

- A web or desktop application.
- Detailed content for every handbook topic.

## Acceptance criteria

1. A first-time reader can identify the purpose, audience, limitations and safe first steps from the Getting Started section.
2. The source remains readable offline and has a documented path to print-friendly use.
3. No foundation content depends on an application or vendor account.

## Dependencies and decisions

- Requires [002](002-privacyAndSecurityModel.md).
- Enables 003, 004, 005 and 006.
- ADRs: [ADR-0001](../../adr/001-handbookBeforeSoftware.md), [ADR-0002](../../adr/002-offlineFirst.md), [ADR-0004](../../adr/004-publicTemplatesPrivateData.md), [ADR-0008](../../adr/008-handbookAsProjection.md).
- Open question: which open source format should be the canonical printable source?

## Verification

- Content review of purpose, audience, limits and safe first steps.
- Offline source and representative print review.
- Dependency review for application or vendor coupling.

## Traceability

- Implementation: [Getting Started](../../../handbook/01-GettingStarted.md)
- Tests: pending
- Documentation: [product vision](../../../documentation/productVision.md)
- Pull request: pending
- Agent runs: None

## Change history

- 2026-07-22: created as `HB-001-HandbookFoundation.yaml`.
- 2026-07-28: migrated to permanent numeric Markdown path; outcome and evidence retained.
