# 003: Handbook content structure

Legacy ID: `HB-003`  
Priority: high  
Owner: project maintainers

## Status

ToDo

## Outcome

As a handbook owner or contributor, I need predictable, safe and adaptable
sections so that information is easy to find and maintain without duplication
or jurisdiction lock-in.

## Context

The eleven existing chapters need a shared structure derived from one
technology-independent domain model. Prompts should explain value, safe content
and review timing while keeping classifications visible.

## Scope

- Section taxonomy, prompt pattern, cross-references and optionality.
- Jurisdiction-neutral core with separable UK-specific guidance.
- Consistent accessible headings, terminology and glossary links.
- Mapping existing chapters to primary sections and domain concepts.

## Out of scope

- Fully authored guidance for every topic.
- Application navigation or data-entry screens.

## Acceptance criteria

1. Every existing chapter topic maps to a primary section and duplicate concepts are identified.
2. A representative chapter follows the agreed prompt pattern and passes privacy and plain-language review.
3. UK-specific concepts can be replaced without changing the core household domain structure.
4. Specialised terms link to plain-language definitions and identify jurisdiction differences.
5. Every section has a reviewed default classification and stricter field classifications are explicit.
6. Every topic maps to a documented domain concept or identifies a reviewed model gap.

## Dependencies and decisions

- Requires [001](001-handbookFoundation.md) and [002](002-privacyAndSecurityModel.md); enables 004, 005 and 006.
- ADRs: [ADR-0005](../../adr/005-informationClassification.md), [ADR-0007](../../adr/007-knowledgeBeforeDocuments.md), [ADR-0008](../../adr/008-handbookAsProjection.md).
- Open questions: the form of emergency information and the primary home for overlapping contacts.

## Verification

- Content inventory, exemplar review, portability review, glossary/link review, classification inventory and domain mapping review.

## Traceability

- Implementation: [handbook](../../../handbook/01-GettingStarted.md)
- Tests: pending
- Documentation: [domain model](../../../documentation/domainModel.md), [glossary](../../../documentation/glossary.md), [information classification](../../../documentation/informationClassification.md)
- Pull request: pending
- Agent runs: None

## Change history

- 2026-07-22: created as `HB-003-HandbookContentStructure.yaml`.
- 2026-07-28: migrated to permanent numeric Markdown path; outcome and evidence retained.
