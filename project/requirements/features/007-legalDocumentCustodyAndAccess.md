# 007: Legal document custody and access

Priority: high
Owner: project maintainers

## Status

ToDo

## Outcome

As a Clann member or attorney, I need to find authoritative wills, powers of
attorney, custodians, copies and official-service references so that authorised
people can locate the right records without Eolas becoming a credential store.

## Context

Legal records need to distinguish authoritative custody from local copies,
represent parties independently of household membership, and separate a
jurisdiction-neutral model from changing jurisdiction-specific language and
services. References and precise locations are sensitive even when they are not
authentication secrets.

## Scope

- Distinct wills and powers of attorney with stable references.
- One authoritative custody location and labelled physical or digital copies.
- Referenced professional custodians, households and protected locations.
- Jurisdiction, instrument type, status, grantors and attorneys.
- Official-service identifiers and safe references to external access arrangements.
- Multiple instruments for different grantors or authority types.

## Out of Scope

- Storing document contents by default or treating a copy as authoritative.
- Passwords, PINs, recovery codes, tokens or authentication secrets.
- Legal advice, inferred authority or an assumed online service in every jurisdiction.

## Acceptance criteria

1. A fictional scenario records a solicitor-held original will and a labelled home copy without duplicating the document or professional.
2. A fictional scenario records two grantors appointing the same attorney through separate instruments.
3. A fictional power-of-attorney record identifies an official service and non-real account and reference placeholders without authentication secrets.
4. Canonical grantor and attorney roles can be presented appropriately for England and Wales, Scotland and Northern Ireland.
5. Automated and manual repository review finds no credential field or usable secret introduced by the feature.

## Dependencies and decisions

- Requires [002](002-privacyAndSecurityModel.md) and [003](003-handbookContentStructure.md); related to 004, 005 and 006.
- ADRs: [002](../../adr/002-offlineFirst.md), [003](../../adr/003-neverStorePasswords.md), [005](../../adr/005-informationClassification.md), [006](../../adr/006-sharedDomainModel.md), [007](../../adr/007-knowledgeBeforeDocuments.md), [008](../../adr/008-handbookAsProjection.md).
- Open questions: initial statuses and copy types; whether service access is an Account or Document-owned metadata; initial jurisdiction-specific instrument types and authority scopes.

## Verification

- Domain-model and fictional scenario tests.
- Jurisdiction presentation tests.
- Automated and manual prohibited-credential review.

## Traceability

- Implementation: pending
- Tests: pending
- Documentation: [domain model](../../../documentation/domainModel.md), [glossary](../../../documentation/glossary.md), [information classification](../../../documentation/informationClassification.md), [privacy and security](../../../documentation/privacyAndSecurity.md), [Legal Affairs](../../../handbook/04-LegalAffairs.md), [Digital Life](../../../handbook/08-DigitalLife.md)
- Pull request: pending
- Agent runs: None

## Change history

- 2026-07-26: created as `APP-001-LegalDocumentCustodyAndAccess.yaml`.
- 2026-07-28: migrated during integration to permanent numeric Markdown path.
