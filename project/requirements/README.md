# Requirements workflow

This directory is the source of truth for specific outcomes clanneolas.com
intends to deliver and why. Requirements can govern handbook content, project
processes or future software. They describe outcomes and constraints before
implementation and must distinguish current behaviour from planned work.

## Directory layout

- `../project.yaml` defines the shared purpose, scope, principles, risks and
  milestones for the wider project.
- `../../docs/principles.md` explains the north-star principles referenced by
  stable ID from each requirement.
- `features/` contains active feature requirements.
- `../adr/` contains architecture decision records (ADRs) that affect multiple
  requirements.
- `completed/` contains completed or retired requirements without erasing their
  history.
- `templates/featureRequirement.yaml` is copied when proposing a feature.
- `../reviews/` contains point-in-time assessments and reviews.

## Workflow

1. **Propose:** copy the feature template into `features/`, assign the next
   stable ID and set `status: proposed`. Describe the user need, scope,
   acceptance criteria, privacy impact, dependencies and open questions. Link
   at least one persona and explain the concrete benefit to them.
2. **Review:** check the proposal against `../project.yaml`, existing requirements
   and handbook content. Resolve material questions or record an ADR under
   `../adr/`. Apply the ADR-0007 keystone test: “Am I modelling knowledge, or am
   I modelling a document?” A reviewed requirement may become `approved`.
3. **Implement:** change the status to `inProgress`, update `traceability` with
   the documents or code being changed, and keep implementation notes factual.
   Do not claim acceptance criteria are met until evidence exists.
4. **Verify:** review every acceptance criterion and record concise evidence in
   `verification`. A requirement with unmet criteria remains `inProgress` or
   becomes `blocked`.
5. **Complete:** set `status: completed`, add `completedDate` and final
   verification, then move the file to `completed/` in the same change. Use a
   version-control move so history is retained; do not reuse its ID.

A requirement that is no longer wanted is set to `retired`, given a reason,
and moved to `completed/`. Superseding requirements link to the retired ID.

## Naming conventions

- YAML and Markdown filenames generally use camelCase, except `README.md` and
  records whose stable identifier is deliberately exposed in the filename.
- Requirement IDs use a short area prefix and a three-digit sequence. Current
  and anticipated namespaces include `HB` (handbook), `APP` (application),
  `DOC` (documentation) and `WEB` (website). Adding a namespace requires review
  to avoid overlapping meanings.
- Feature files use `<ID>-<Name>.yaml`, for example
  `HB-001-HandbookFoundation.yaml`. This mirrors ADR filenames, makes the stable
  ID visible and keeps related records together when sorted. IDs are permanent;
  descriptive names may be clarified later.
- ADR files use `ADR-<fourDigitNumber>-<shortName>.md`, for example
  `ADR-0005-canonicalFormat.md`. The established ADR prefix and number take
  precedence over the general camelCase filename convention.
- YAML keys use camelCase. Dates use ISO 8601 `YYYY-MM-DD` format.
- Requirements use normative words deliberately: **must** is mandatory,
  **should** is the expected default, and **may** is optional.

## Priority and status

Priorities are `critical`, `high`, `medium` or `low`. `critical` is reserved
for safety, privacy or foundational work that blocks responsible progress.

Valid statuses are:

- `proposed`: written but not yet accepted for implementation;
- `approved`: reviewed and ready to implement;
- `inProgress`: implementation or verification is under way;
- `blocked`: cannot proceed until a recorded dependency or question is
  resolved;
- `completed`: all acceptance criteria have evidence;
- `retired`: deliberately closed without implementation or replaced.

## Review expectations

Reviewers should look for duplicate requirements, contradictions, accidental
UK or vendor coupling, private data, inaccessible language and claims that get
ahead of implementation. A feature without a credible benefit to at least one
documented persona is not ready for approval. Reviewers must also test the
outcome against every linked principle rather than treating principle IDs as
labels. Changes to project principles require explicit review and normally an
ADR. Feature requirements should link both to the
project principles they satisfy and to the relevant handbook, documentation,
tests or future code paths.

Presentation requirements are legitimate when they concern matters such as
readability, navigation, accessibility or print layout. They must describe a
projection of shared knowledge rather than introduce a competing source of
truth.

No requirement file contains private household data. Fictional examples must
be clearly labelled, safe to publish and free of usable credentials or
realistic identifiers.
