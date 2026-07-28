# 002: Privacy and security model

Legacy ID: `HB-002`  
Priority: critical  
Owner: project maintainers

## Status

ToDo

## Outcome

As a handbook owner or trusted reader, I need clear rules for what to record
and what only to reference, so that the handbook does not create avoidable
privacy or security harm.

## Context

The public project and private household copies need an explicit boundary.
Guidance must cover classification, minimisation, safe references, access,
storage, sharing, backup and disposal without guaranteeing a storage method.

## Scope

- Public, Private, Confidential and Highly Confidential classification.
- Paper and digital safeguards, including stricter field-level classification.
- Safe references to protected documents and credential stores.
- Explicitly fictional, publishable examples.

## Out of scope

- Guaranteeing the security of a chosen storage method.
- Storing or managing passwords, PINs, recovery codes or similar secrets.

## Acceptance criteria

1. A section author can classify every proposed field using the documented model.
2. A repository scan finds no real household data, passwords, PINs or recovery codes in examples.
3. Guidance covers paper and digital storage, controlled sharing, backup and secure disposal without mandating a vendor.
4. The classification guide defines allowed values, ordering, examples, handling rules and a safe default for missing classifications.

## Dependencies and decisions

- Enables 001, 003, 004, 005 and 006.
- ADRs: [ADR-0003](../../adr/003-neverStorePasswords.md), [ADR-0004](../../adr/004-publicTemplatesPrivateData.md), [ADR-0005](../../adr/005-informationClassification.md).
- Open question: should private copies live outside the repository by default or in a prominently warned ignored directory?

## Verification

- Classification exercise and model review.
- Manual and automated prohibited-data review.
- Content review for storage, sharing, backup and disposal coverage.

## Traceability

- Implementation: pending
- Tests: pending
- Documentation: [information classification](../../../documentation/informationClassification.md), [privacy and security](../../../documentation/privacyAndSecurity.md)
- Pull request: pending
- Agent runs: None

## Change history

- 2026-07-22: created as `HB-002-PrivacyAndSecurityModel.yaml`.
- 2026-07-28: migrated to permanent numeric Markdown path; outcome and evidence retained.
