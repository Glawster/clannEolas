# ADR-0002: Offline first

- Status: accepted
- Date: 2026-07-22
- Related requirements:
  - [001](../requirements/features/001-handbookFoundation.md),
  - [005](../requirements/features/005-annualReviewProcess.md)

## Context

The handbook may be needed during an internet outage, account-access problem,
emergency or after the person who maintained it can no longer help. Requiring a
network service would add an avoidable point of failure and potential vendor
dependency.

## Decision

Core handbook content and essential workflows will work offline where
practical. Online services may provide optional convenience later, but they
must not be required to read, maintain or print the core handbook.

## Consequences

- Open local files and print-friendly output are first-class formats.
- Essential guidance cannot depend on live links or online authentication.
- Any future online integration needs an offline fallback or a documented
  non-essential role.
- Users remain responsible for protecting offline paper and digital copies.
