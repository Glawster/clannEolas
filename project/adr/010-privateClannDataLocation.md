# ADR-0010: Private Clann data location

- Status: superseded
- Date: 2026-07-28
- Accepted: 2026-07-28
- Approved by: project maintainer
- Related requirements: [002](../requirements/features/002-privacyAndSecurityModel.md), [001](../requirements/features/001-handbookFoundation.md)
- Superseded by: [011](011-platformPrivateDataRoot.md)

## Context

The public repository contains reusable guidance, templates, code and approved
fictional examples. A real Clann record contains private or confidential
household knowledge and must not be placed inside the repository, even in an
ignored directory. Ignored paths reduce accidental staging but do not provide
access control, encryption, backup safety or a clear conceptual boundary.

The current bootstrap tool already creates a structured Clann tree containing
YAML records. A stable application-managed location is needed so command-line,
desktop, mobile, web and automation interfaces can share one storage convention
without asking ordinary users to select or understand filesystem paths.

## Decision

Store application-managed private digital Clann records outside the public
repository beneath:

```text
~/eolas/clanns/<clannSlug>/
```

Interfaces must derive this location from the current user's home directory and
must not ask an ordinary user to choose a repository-relative data directory.
Core services may accept an explicit root for isolated testing, controlled
migration or administrator-managed integration, but user-facing production
workflows use `~/eolas/clanns/` by default and must validate that they do not
write private records into the public project.

The location is a privacy boundary, not a security guarantee. Guidance and
interfaces must still address operating-system access, device protection,
sharing, backup, recovery, retention and secure disposal. Passwords, PINs,
recovery codes and equivalent secrets remain prohibited regardless of location.

Explicit user exports are separate derived copies. Before creating an export,
the interface must identify its classification, destination and handling risk;
an export must never silently become a second canonical record.

## Alternatives considered

### An ignored directory inside the repository

Rejected. Ignore rules are easy to bypass, repository tools expose confusing
paths, and the arrangement weakens the public-project/private-household boundary.

### Ask every user to choose a data directory

Rejected as the normal workflow because it exposes filesystem decisions to
ordinary users and creates inconsistent storage. Controlled overrides remain
available only for testing, migration and managed integration.

### A vendor cloud account

Rejected as a requirement. A future optional synchronisation service must not
replace the local, vendor-neutral location or offline access.

## Consequences

- Public source and private household records have different default roots.
- User-facing tools can find Clann records without exposing path selection.
- Repository ignore rules remain defence in depth, not the primary boundary.
- Tests use temporary roots and must contain only conspicuously fictional data.
- Backup and export features must treat copies as classified private data and
  prevent silent divergence from the canonical structured record.
- The location alone does not encrypt data or restrict access; those controls
  require explicit guidance and, where appropriate, separate requirements.

## Supersession

Superseded on 2026-07-28 by ADR-0011. The fixed `~/eolas/clanns/` location
remains the initial CLI convention, but it is not portable to Windows, macOS,
mobile application sandboxes or browser-managed local storage.
