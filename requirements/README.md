# Requirements workflow

This directory is the source of truth for what familyHandbook intends to
deliver and why. Requirements describe outcomes and constraints before content
or software is implemented. They must distinguish current behaviour from
planned work.

## Directory layout

- `project.yaml` defines the shared purpose, scope, principles, risks and
  milestones.
- `features/` contains active feature requirements.
- `decisions/` contains durable decisions that affect multiple requirements.
- `completed/` contains completed or retired requirements without erasing their
  history.
- `templates/featureRequirement.yaml` is copied when proposing a feature.
- `repositoryAssessment.md` records the baseline from which this workflow was
  introduced.

## Workflow

1. **Propose:** copy the feature template into `features/`, assign the next
   stable ID and set `status: proposed`. Describe the user need, scope,
   acceptance criteria, privacy impact, dependencies and open questions.
2. **Review:** check the proposal against `project.yaml`, existing requirements
   and handbook content. Resolve material questions or record a decision under
   `decisions/`. A reviewed requirement may become `approved`.
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

- YAML and Markdown filenames use camelCase, except the conventional
  `README.md`.
- Feature files use `fh<number><ShortName>.yaml`, for example
  `fh001HandbookFoundation.yaml`. IDs inside the files are uppercase and
  permanent; names may be clarified later.
- Decision files use `dec<number><ShortName>.md`, for example
  `dec001CanonicalFormat.md`, and link to affected feature IDs.
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
ahead of implementation. Changes to project principles require explicit review
and normally a decision record. Feature requirements should link both to the
project principles they satisfy and to the relevant handbook, documentation,
tests or future code paths.

No requirement file contains private household data. Fictional examples must
be clearly labelled, safe to publish and free of usable credentials or
realistic identifiers.
