# 003: Handbook content structure

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

1. A content inventory lists every heading in the eleven existing handbook
   chapters, assigns each topic one primary handbook section, records every
   secondary cross-reference, and identifies repeated knowledge that must not
   be maintained as separate values.
2. At least one representative chapter is rewritten using a documented prompt
   pattern that states why the information is useful, what to record or safely
   reference, what not to record, its review trigger or interval, whether the
   topic is optional, and its visible classification. A privacy reviewer and a
   plain-language reviewer record pass/fail results and actionable findings
   against that exemplar.
3. A portability review separates the jurisdiction-neutral concept and prompt
   from any UK-specific term, procedure or external guidance in every inventoried
   topic. Replacing one representative UK guidance block with a documented
   non-UK placeholder must require no change to the core domain concepts or the
   chapter taxonomy.
4. Every specialised term used by the exemplar links to a plain-language
   glossary definition. Each definition either describes known jurisdictional
   differences or explicitly states that none have yet been identified, and a
   link check finds no missing local glossary target.
5. A classification inventory gives every section a reviewed default from the
   four levels in 005, lists each field or block that needs a stricter
   classification, and records the reviewer and outcome. No field may be made
   less restrictive than its section, and Highly Confidential values must be
   replaced by safe references rather than requested as handbook content.
6. A domain mapping links every inventoried topic to one or more concepts in
   `documentation/domainModel.md`, distinguishes projection headings from
   domain concepts, and records any unmapped topic as an explicit model gap.
   Each gap must have a recorded review outcome before this requirement can be
   completed.

## Dependencies and decisions

- Requires [001](001-handbookFoundation.md) and [002](002-privacyAndSecurityModel.md); enables 004, 005 and 006.
- ADRs: [005](../../adr/005-informationClassification.md), [007](../../adr/007-knowledgeBeforeDocuments.md), [008](../../adr/008-handbookAsProjection.md).
- Proposed resolution, pending stakeholder approval: emergency information is
  a concise projection of shared household knowledge, not a separately
  maintained set of values. The handbook may explain and cross-reference that
  projection; the eventual output format is outside this requirement.
- Proposed resolution, pending stakeholder approval: a contact is maintained
  once as the domain concept defined in `documentation/domainModel.md` and may
  be projected into several handbook sections. The inventory assigns a primary
  handbook section for navigation and uses cross-references everywhere else;
  section placement does not make that chapter the source of truth.

## Verification

| Criterion | Repeatable evidence |
| --- | --- |
| 1 | Compare an inventory row set with all level 1–3 headings in the eleven handbook files; review primary-section, cross-reference and duplicate-value columns. |
| 2 | Check the exemplar against every prompt-pattern element; retain named privacy and plain-language review outcomes and findings. |
| 3 | Review every inventory row for neutral core and jurisdiction-specific guidance; perform and record the representative substitution exercise. |
| 4 | Extract specialised terms and verify their local glossary targets; review the jurisdiction statement for each definition. |
| 5 | Check every inventoried section against the four allowed levels, reviewer outcome and any stricter field/block override; search prompts for prohibited Highly Confidential values. |
| 6 | Check that every inventory row has a domain-concept link or a reviewed gap outcome, and that projection-only headings are not presented as domain concepts. |

## Traceability

- Implementation: [handbook](../../../handbook/01-GettingStarted.md)
- Tests: pending
- Documentation: [domain model](../../../documentation/domainModel.md), [glossary](../../../documentation/glossary.md), [information classification](../../../documentation/informationClassification.md)
- Pull request: pending
- Agent runs: None

## Change history

- 2026-07-22: created as `HB-003-HandbookContentStructure.yaml`.
- 2026-07-28: migrated to permanent numeric Markdown path; outcome and evidence retained.
- 2026-07-29: refined acceptance criteria and repeatable evidence; proposed
  emergency-projection and single-contact-source resolutions for stakeholder
  approval.
