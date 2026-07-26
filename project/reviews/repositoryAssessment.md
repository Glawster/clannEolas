# Repository assessment

Assessment date: 2026-07-22. Baseline: `development` at `f6d1702`, plus the
pre-existing untracked, empty `requirements/featureRequirement.yaml` and
`requirements/project.yaml` files.

## What exists

- Eleven short handbook chapter outlines covering getting started, emergencies,
  family and care, legal affairs, money, home, health, digital life, final
  wishes, family knowledge and annual review.
- Empty placeholders for vision, design, privacy, roadmap, application,
  changelog and licence content.
- Empty template directories for an emergency summary and fictional example.
- General Python-oriented Copilot guidance and repository-specific guidance
  that appears to have been copied from unrelated chapter-based projects.
- No application source, build framework, dependency manifest, test suite or
  automated validation. This is consistent with the current content-first
  stage, although the empty `app/` directory can imply more progress than
  exists.

## Strengths

- The handbook outline covers both conventional practical records and easily
  lost family knowledge such as routines, recipes and traditions.
- Emergency, care, legal, financial, property, health and digital topics form a
  useful starting inventory.
- A dedicated annual review chapter recognises that information becomes stale.
- Markdown is open, readable offline, versionable and compatible with future
  print workflows.
- The repository is small enough to establish traceability before content or
  software grows.

## Missing foundations

- A stated public purpose, audience, scope, exclusions and non-negotiable
  project principles.
- A privacy model explaining data minimisation, classification, storage,
  sharing, backup, disposal and the boundary between public templates and
  private copies.
- Content standards for prompts, accessibility, print use, jurisdiction
  layering and professional-advice boundaries.
- Approved requirements, ADRs, acceptance evidence and traceability.
- A clearly fictional, privacy-reviewed example household.
- A licence decision and actual licence text; the current `LICENSE` file is
  empty, so the repository should not yet claim a specific open-source licence.
- Link and YAML validation automation. No software framework exists to validate.

## Inconsistencies and duplication

- Emergency contacts overlap between the emergency plan and family-and-care
  chapters; contact ownership and cross-referencing need a decision.
- Password managers and two-factor authentication are useful topics, but the
  outline does not yet warn against recording passwords, PINs or recovery
  codes.
- Annual-review topics mirror several chapters without yet defining whether the
  review page links to those chapters or duplicates their data.
- The existing handbook filenames use zero-padded numeric prefixes and
  PascalCase topic names. That established convention conflicts with the new
  camelCase default, so it is retained pending an explicit migration decision.

## Guidance conflicts

The master Copilot instructions say living documentation belongs under
`documentation/`, while this repository uses `docs/` for handbook guidance and
`project/` for planning and governance. The repository-specific
instructions also describe unrelated top-level domains such as football
manager, walking football and Linux, and prescribe `chapters/` directories that
do not match this repository's `handbook/` structure. These rules should be
corrected separately; this change does not move useful existing content merely
to satisfy conflicting boilerplate.

The project area complements the existing handbook: requirements govern why
and how content changes, while vision, roadmap, ADRs and reviews provide
the wider planning context. `handbook/` remains the user-facing content area.
No current feature requirement is marked completed.
