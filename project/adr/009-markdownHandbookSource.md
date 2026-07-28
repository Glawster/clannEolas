# ADR-0009: Markdown as the canonical handbook source

- Status: accepted
- Date: 2026-07-28
- Accepted: 2026-07-28
- Approved by: project maintainer
- Related requirements: 
[001](../requirements/features/001-handbookFoundation.md), 
[003](../requirements/features/003-handbookContentStructure.md), 
[006](../requirements/features/006-gettingStartedGuide.md)

## Context

Requirement 001 needs an open, human-readable canonical source for the handbook
projection and a repeatable path from that source to print. The format must be
readable offline without specialist software, work well with version control,
avoid vendor or account dependencies and support accessible printed output.

The repository already authors handbook chapters in Markdown. Markdown is also
identified in the repository assessment as open, offline-readable, versionable
and compatible with future print workflows. PDF is useful for distribution and
printing but is difficult to maintain as source. A word-processor or publishing
format could offer richer page design but would introduce application-specific
behaviour and a less reviewable source.

ADR-0007 and ADR-0008 require an important boundary: the handbook is a
projection of household knowledge, not the underlying knowledge model. Choosing
a handbook source format must not make document headings or Markdown structure
the canonical household data model.

The existing Clann bootstrap implementation already serialises structured
private household records as UTF-8 YAML beneath `~/eolas/clanns/`. These include
Clann, household, person and identity records. That YAML and the Markdown
handbook have different responsibilities and must not be described as competing
copies of the same document.

## Decision

Use UTF-8 Markdown as the canonical source format for the handbook projection.
Keep handbook source files under `handbook/` using the repository's established
chapter naming convention and relative links for repository-owned material.

The Markdown source is deliberately both human-editable and tool-manipulable.
Automation and web, mobile, desktop or command-line interfaces may create,
read, validate and update Markdown files. For a private completed handbook,
those tools may read structured household knowledge from YAML and project it
into Markdown. Updates to structured values must be applied through shared core
logic to the structured record and then reflected in the projection, rather
than becoming independently maintained values in both formats. Interface layers
orchestrate the workflow; they do not own either content model.

Markdown is an implementation and durability format, not a skill expected of
ordinary users. User-facing interfaces must present concepts, questions,
validation and review actions in plain language while handling Markdown syntax,
paths, filenames and safe file updates internally. Direct Markdown editing is
retained for contributors, advanced users, interoperability and recovery, but
is not the normal completion or maintenance workflow.

PDF and paper are derived handbook experiences, not canonical sources. A
documented, locally runnable renderer may transform Markdown into a
representative print form. The project does not select a permanent renderer in
this ADR: a renderer may change without changing the canonical source, provided
the verified output preserves content, hierarchy, safety warnings and
classification labels.

Essential handbook content must remain understandable from the Markdown source
without a network connection. Online links may supplement it but must not be
the only location of information required to understand or safely use the
handbook.

Markdown structures presentation of the handbook projection only. They do not
define the canonical household-knowledge model, storage schema or future
application interface.

The current format relationship is:

```text
Public guidance (Markdown) + private structured records (YAML)
                              ↓ projection
                    household handbook (Markdown)
                              ↓ rendering
                         PDF or paper
```

This ADR standardises the Markdown handbook layer only. It acknowledges YAML as
the current private structured-record serialisation but does not make YAML the
permanent canonical knowledge-storage decision. That decision requires its own
requirement and ADR covering schema evolution, round trips, validation,
concurrency, migration and recovery.

## Alternatives considered

### PDF as canonical source

Rejected because PDF is appropriate for fixed output but poor as a reviewable,
maintainable source and normally requires a separate authoring format.

### Word-processor or desktop-publishing files

Rejected as the canonical source because application-specific formats and
layout behaviour weaken vendor independence, text review and durable offline
access.

### YAML as the subject of this ADR

Rejected as an expansion of this decision. YAML is already used for current
private structured records, but ADR-0007 and ADR-0008 keep that storage concern
separate from the handbook projection. Requirement 001 does not settle whether
YAML, JSON, SQLite or another format is the permanent knowledge store.

## Consequences

- Contributors can read and review the canonical handbook with an ordinary text
  editor and standard version-control tools.
- People may maintain the handbook directly in Markdown or through optional
  automation, web, mobile, desktop or CLI interfaces operating on those files.
- Ordinary users do not need to know that Markdown is being manipulated and
  are not required to edit files, choose paths or understand Markdown or YAML
  source structure.
- Tooling must distinguish updates to structured YAML knowledge from updates to
  Markdown presentation and free-form guidance, then regenerate affected
  projections without creating independently maintained duplicate values.
- Every interface must preserve unknown supported content, write valid UTF-8
  Markdown safely and avoid creating an interface-specific source of truth.
- Print workflows must render from Markdown and document their local command,
  dependencies and representative review evidence.
- Generated PDF or other print exports normally belong under `output/` and are
  not committed unless a separate requirement approves publication.
- Markdown features that require one vendor-specific renderer should be avoided
  or given a portable fallback.
- Print layout quality still requires explicit accessibility and representative
  output checks; choosing Markdown does not prove print quality by itself.
- YAML remains the implemented serialisation for the initial private Clann
  records, while the permanent household-knowledge storage contract remains an
  independent decision.

## Approval

Accepted by the project maintainer on 2026-07-28. Requirement 001 remains in
`ToDo` until its remaining dependency and readiness checks are satisfied.
