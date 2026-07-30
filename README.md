# clanneolas.com

An open-source, privacy-conscious project for creating a practical record of the
information a family may need during an emergency, serious illness, loss of
capacity or death.

The repository is at an early, content-first stage. It currently contains a
draft handbook outline and project requirements; it does not contain a working
web or desktop application. The handbook is intended to remain useful as
human-readable and printable documents without future software.

## Documentation

- [Repository layout](.github/repositoryLayout.md)
- [Requirements management](.github/requirementsManagement.md)
- [Product vision](documentation/productVision.md)
- [Project principles](documentation/principles.md)
- [Design principles](documentation/designPrinciples.md)
- [Personas](documentation/personas/README.md)
- [Glossary](documentation/glossary.md)
- [Information classification](documentation/informationClassification.md)
- [Privacy and security](documentation/privacyAndSecurity.md)
- [Domain model](documentation/domainModel.md)
- [Project planning and governance](project/README.md)
- [Requirements workflow](project/requirements/README.md)
- [Repository assessment](project/reviews/repositoryAssessment.md)
- [Change log](documentation/changeLog.md)
- [Brand assets and guidance](brand/README.md)
- [Handbook outline](handbook/01-GettingStarted.md)

## Publishing website assets

The development repository is the source of truth for website assets. The
[`publish-assets.yml`](publish-assets.yml) manifest maps selected source folders
to folders in the separate public website repository. Each target folder is
managed as a complete mirror: files removed from its source are removed from
that target, but the publisher never changes content outside configured target
folders.

Preview a publication before applying it:

```bash
scripts/publish-assets.sh --verbose
```

Publish to the default website checkout at `~/Source/clanneolasWebsite`:

```bash
scripts/publish-assets.sh --confirm
```

Commit the published paths, or commit and push them:

```bash
scripts/publish-assets.sh --confirm --commit
scripts/publish-assets.sh --confirm --push
```

Both repositories must normally have clean working trees. `--force` overrides
that check; it does not broaden the folders the script may change. For a
checkout in another location, use `--destination PATH` or set
`CLANN_EOLAS_WEBSITE_REPO`. An alternative manifest can be selected with
`--manifest PATH`. The publisher requires Bash, Git, rsync, Python 3, and the
project-standard `organiseMyProjects` package providing `logUtils.sh`.

The manifest accepts this intentionally small YAML structure:

```yaml
publish:
  - source: brand/logo
    target: assets/logos
```

Source and target paths must be relative, source folders must exist, and target
folders may not overlap. `.git`, `.github`, `.vscode`, `documentation`,
`deploy`, `scripts`, `README.md`, and `LICENSE` are excluded from mapped trees
unless one is itself explicitly selected as a source mapping. Publishing is a
safe preview unless `--confirm` is supplied. `--push` implies `--commit`, and
both options require `--confirm`.

Do not put real household data, passwords, PINs, recovery codes or other
secrets in this public repository. Examples must be fictional.
