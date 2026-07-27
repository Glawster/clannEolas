# Repository layout

This guide explains what belongs in each top-level directory and where to put
new material. It is written as a reusable template: copy it into another
project, retain the common rules, and replace the project-specific directory
rows and examples.

The central convention is to keep project-management records separate from the
durable documentation and content that a project produces.

## Choosing between `project/` and `documentation/`

Use `project/` for records about planning, governing and delivering the work.
Use `documentation/` for maintained explanations of the product, its domain
and the principles contributors need to understand it. These two directories
form the reusable core of this layout.

A useful test is:

- if the document answers **what have we decided, committed to, reviewed or
  scheduled?**, put it in `project/`;
- if it answers **what is Eolas, how does it work, or what does a contributor
  need to understand?**, put it in `documentation/`.

For example, a proposed outcome belongs in `project/requirements/`. A durable
explanation of the resulting behaviour belongs in `documentation/`. A choice
between competing approaches and its consequences belongs in `project/adr/`.
Do not duplicate the same explanation in both places: link to the authoritative
document instead.

## Top-level directories

| Path | Purpose | Examples |
| --- | --- | --- |
| `app/` | User-facing application code and application-specific resources, when the project has an application. | Screens, application entry points and UI orchestration. |
| `brand/` | Approved visual identity assets and guidance. | Logos, icons, imagery, colours and the style guide. |
| `data/` | Structured, non-secret data used by the project. | Schemas, safe fixtures and clearly fictional example households. |
| `documentation/` | Living product, domain and contributor documentation. | Product vision, principles, personas, glossary, domain model, privacy model and this guide. |
| `eolas/` | Reusable core and domain code, independent of a particular UI. Rename this directory for the project. | Household knowledge models, validation and transformations. |
| `handbook/` | The human-readable and printable handbook content. | Getting started, emergency planning and annual review chapters. |
| `project/` | Planning, governance and historical delivery records. | Requirements, ADRs, roadmap and point-in-time reviews. |
| `scripts/` | Maintainer tools and repeatable development tasks. | Asset-generation and repository-maintenance scripts. |
| `tests/` | Automated tests, arranged to mirror the code they verify. | Tests for modules under `eolas/` and application behaviour. |

Generated output, local caches, virtual environments, secrets and real
household data do not belong in version control. A routine that creates output
files should write them beneath a root-level `output/` directory, which should
normally be ignored unless an export is deliberately approved for publication.

## Inside `project/`

| Path | Purpose |
| --- | --- |
| `project/project.yaml` | Current project purpose, scope, audience, risks and milestones. |
| `project/requirements/features/` | Proposed, approved or in-progress outcomes and constraints. |
| `project/requirements/completed/` | Completed or retired requirements retained for traceability. |
| `project/requirements/templates/` | Templates used to create consistent project records. |
| `project/adr/` | Significant project-shaping decisions and their consequences. |
| `project/reviews/` | Point-in-time assessments that should not be mistaken for living guidance. |
| `project/roadmap.md` | Current sequencing and priorities. |

The detailed workflows and naming rules live in the
[requirements guide](../project/requirements/README.md) and
[ADR guide](../project/adr/README.md).

## Documentation conventions

- Keep only `README.md` as the main documentation entry point at the repository
  root; place other maintained guides under `documentation/` or the directory
  whose contents they introduce.
- Use camelCase Markdown filenames, except for `README.md` and records with a
  stable identifier such as an ADR or requirement.
- Put a directory-specific `README.md` in a directory when readers need an
  index or instructions for working with its contents.
- Keep Mermaid source (`.mmd`) beside the document or subject it explains.
- Link from the root README to living guides so contributors can discover them.
- Prefer relative links so documentation works both locally and on GitHub.

## Reusing this template

When adopting this layout in another repository:

1. copy this file to `documentation/repositoryLayout.md`;
2. keep the `project/` versus `documentation/` distinction unless the project
   has a documented reason to use a different model;
3. replace `eolas/` with the new project's source-package directory;
4. remove optional rows such as `app/`, `brand/`, `data/` or `handbook/` when
   they do not apply, and add rows for genuine top-level concerns;
5. update the placement examples so they use the new project's vocabulary;
6. link the guide from the new project's root `README.md`.

Avoid copying empty directories merely to resemble this repository. Each
top-level directory should represent a real, distinct responsibility.

## Placement examples

| New item | Location | Reason |
| --- | --- | --- |
| A proposal for handbook search | `project/requirements/features/` | It describes an outcome not yet necessarily delivered. |
| The decision to use a particular search approach | `project/adr/` | It records a consequential choice and rationale. |
| An explanation of the implemented search model | `documentation/` | It is maintained product or technical knowledge. |
| A review of privacy risks on a particular date | `project/reviews/` | It is a point-in-time assessment. |
| The current privacy and security model | `documentation/privacyAndSecurity.md` | It is living guidance. |
| A chapter that families will read or print | `handbook/` | It is part of the product's handbook content. |
| A fictional household fixture used by tests | `data/` | It is structured, safe project data. |
| A command used to regenerate icons | `scripts/` | It is a repeatable maintainer task. |

When a document changes category, move it rather than copying it, update links
in the same change and preserve its version-control history.
