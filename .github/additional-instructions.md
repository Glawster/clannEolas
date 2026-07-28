# Additional agent instructions for clanneolas.com

These repository-specific instructions extend `.github/agent-instructions.md`
and the managed layout in `.github/repositoryLayout.md`.

## Scope

- Keep the master development standards as the default for code changes.
- Use this file for repository structure and content conventions only.

## Repository Layout Conventions

- `handbook/` is a project-specific top-level product-content directory. It
  contains the human-readable and printable handbook chapters.
- Handbook chapter filenames retain their established zero-padded numeric
  prefix and PascalCase topic, for example `01-GettingStarted.md`.
- `app/` is optional and must contain application code only when an application
  is actually being delivered; planned software belongs in requirements.
- Keep repeatable maintainer tools in `scripts/` and do not commit runtime cache
  artifacts.

## Diagram and Document Conventions

- Mermaid source files use `.mmd` and should live with the relevant chapter content.
- Preserve existing naming conventions for chapter diagram files.
- Generated exports should not be committed unless there is an explicit requirement.

## Change Discipline

- Prefer moving/renaming existing files over delete-and-recreate when restructuring content.
- When changing structure, keep chapter numbering and path style consistent across all domains.
- Keep `.gitignore` aligned with generated artifacts introduced by scripts or export workflows.
