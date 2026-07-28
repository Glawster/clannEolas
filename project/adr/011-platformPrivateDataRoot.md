# ADR-0011: Platform-resolved private data root

- Status: accepted
- Date: 2026-07-28
- Accepted: 2026-07-28
- Approved by: project maintainer
- Supersedes: [010](010-privateClannDataLocation.md)
- Related requirements: [002](../requirements/features/002-privacyAndSecurityModel.md), [001](../requirements/features/001-handbookFoundation.md)

## Context

ADR-0010 placed application-managed private Clann records beneath
`~/eolas/clanns/`. That is a clear public/private boundary for the initial CLI,
but one literal path is not portable across Linux, Windows, macOS, Android, iOS
and browser-based applications.

Desktop operating systems define different application-data conventions.
Mobile applications normally receive a private sandbox rather than an ordinary
user-selected directory. A browser-only application cannot generally write to
arbitrary local paths and instead uses origin-scoped browser storage or a file
chosen through an explicit user permission flow.

The intended product remains local-first. A web-style interface may be hosted
inside an installed desktop or mobile application, served by a local service,
or delivered as an offline-capable browser application. Interface technology
must not silently change the private data boundary or upload Clann data.

## Decision

Define a logical `eolasDataRoot` resolved by the storage adapter for the active
platform. Application-managed private Clann records live beneath:

```text
<eolasDataRoot>/clanns/<clannSlug>/
```

Default adapters use the operating system's private application-data location:

| Platform | Default storage convention |
| --- | --- |
| Linux | XDG user data location, normally `~/.local/share/Eolas/` |
| macOS | User Application Support location, normally `~/Library/Application Support/Eolas/` |
| Windows | Per-user local application data, normally `%LOCALAPPDATA%\Eolas\` |
| Android and iOS | The application's private operating-system sandbox |
| Browser-only offline application | Origin-private browser storage such as IndexedDB or equivalent managed storage |

The initial CLI may continue using `~/eolas/` until it adopts the shared
platform resolver. That compatibility path is transitional and must not be
copied into new platform interfaces.

All interfaces use a shared storage contract and core validation logic.
Desktop, mobile, web and CLI layers select an adapter and orchestrate user
interaction; they do not embed platform paths or independently implement record
semantics.

Ordinary users are not asked to understand paths, YAML, Markdown or browser
storage. Interfaces expose task-oriented actions such as backup, restore,
export and, where supported, open or move data. Any user-selected location
requires an explicit informed action and validation that it is outside the
public project.

A hosted web service must not receive or persist private Clann data unless a
separate approved requirement and ADR define remote storage, authentication,
encryption, consent, recovery, deletion and operations. A web interface alone
does not imply server-side household-data storage.

## Storage contract

Every adapter must provide equivalent observable behaviour for:

- atomic creation and safe update;
- schema and classification validation;
- refusal to overwrite an unexpected non-empty record;
- enumeration and lookup of Clanns;
- backup, restore and export boundaries;
- migration and recovery reporting; and
- errors that do not disclose private values.

YAML remains the current desktop and CLI serialisation for structured Clann
records. Browser or mobile adapters may use platform-managed structured storage
internally, but imports, exports and projections must preserve the approved
domain semantics. A later requirement may refine the cross-platform storage and
synchronisation contract without changing this local-first privacy boundary.

## Alternatives considered

### Use `~/eolas/` on every platform

Rejected because it ignores platform conventions, mobile sandboxes and browser
capability restrictions.

### Ask users to choose a directory during setup

Rejected as the default because ordinary users should not need to understand
storage paths. An explicit advanced move or export workflow may be supported.

### Store all data on a hosted server

Rejected as the default because it conflicts with offline use and materially
changes the project's privacy, security and operational responsibilities.

### Use browser storage for every interface

Rejected because browser origin storage is not a suitable universal contract
for installed applications, portable backups or direct local recovery.

## Consequences

- New code depends on a logical storage service rather than literal paths.
- Platform adapters require contract tests proving equivalent safety behaviour.
- A locally installed application may use a web-style interface without moving
  private data to a server.
- Browser-only deployments require clear backup, quota, persistence and data-
  clearing warnings.
- Mobile and browser storage may not expose YAML as ordinary files, although
  approved import, export and projection behaviour remains interoperable.
- The initial CLI path requires a future migration to the shared resolver.
- Local storage does not itself provide encryption, access control or backup;
  those controls remain explicit requirements and user guidance.
