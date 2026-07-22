# ADR-0005: Information classification

- Status: accepted
- Date: 2026-07-22
- Related requirements: HB-002, HB-003

## Context

Handbook sections range from publishable instructions to health, financial and
security-related household information. Without a shared vocabulary, authors
may request too much detail, users may misunderstand risk and future software
may apply inconsistent handling rules.

A single classification for the whole handbook is too coarse. A visible section
default is understandable without software, while field-level overrides allow
particularly sensitive information to receive stricter treatment.

## Decision

familyHandbook will use four ordered classifications: `Public`, `Private`,
`Confidential` and `Highly Confidential`.

Every handbook section will declare a default classification. Individual fields
or blocks may use a stricter classification. The most restrictive applicable
classification controls handling.

Highly Confidential values—including passwords, PINs and recovery codes—must
not be stored in ordinary handbook content. The handbook may safely reference a
separate authorised access arrangement.

Labels must remain human-readable. Future structured formats will expose stable
machine-readable values so software can apply warnings and handling rules
without redefining the model.

## Consequences

- Authors must consider the sensitivity of completed content, not only blank
  prompts.
- Existing handbook sections need classification review before the content
  structure is complete.
- Printed and exported output must retain visible classification labels.
- Future software must validate known values and fail safely when metadata is
  absent or invalid.
- Classification reduces ambiguity but does not replace access control, data
  minimisation or user judgement.
