"""Read-only discovery and health summaries for private Clann directories."""

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Tuple

import yaml


@dataclass(frozen=True)
class ClannSummary:
    """Safe metadata needed to list one usable Clann."""

    path: Path
    name: str
    status: str
    people_count: int
    modified: str | None


@dataclass(frozen=True)
class ClannDirectoryIssue:
    """A directory that cannot currently be used as a Clann."""

    path: Path
    reason: str


def clannsInspect(
    data_root: Path,
) -> Tuple[Tuple[ClannSummary, ...], Tuple[ClannDirectoryIssue, ...]]:
    """Discover usable Clanns and explain directories that need attention."""
    clanns_path = data_root.expanduser().resolve() / "clanns"
    if not clanns_path.is_dir():
        return (), ()

    summaries = []
    issues = []
    for path in sorted(item for item in clanns_path.iterdir() if item.is_dir()):
        if path.name == ".wastebasket":
            continue
        summary, issue = _clannInspect(path)
        if summary is not None:
            summaries.append(summary)
        if issue is not None:
            issues.append(issue)
    return tuple(summaries), tuple(issues)


def clannsRemoved(dataRoot: Path) -> Tuple[Path, ...]:
    """Return incomplete Clann directories available for restoration."""
    wastebasketPath = dataRoot.expanduser().resolve() / "clanns" / ".wastebasket"
    if not wastebasketPath.is_dir():
        return ()
    return tuple(sorted(path for path in wastebasketPath.iterdir() if path.is_dir()))


def _clannInspect(path: Path) -> tuple[ClannSummary | None, ClannDirectoryIssue | None]:
    manifest_path = path / "clann.yaml"
    if not manifest_path.is_file():
        return None, ClannDirectoryIssue(path, "missing clann.yaml")
    try:
        document = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as error:
        return None, ClannDirectoryIssue(path, f"cannot read clann.yaml: {error}")
    if not isinstance(document, dict):
        return None, ClannDirectoryIssue(path, "clann.yaml is not a mapping")
    if document.get("schema") != "eolas/clann/v1":
        return None, ClannDirectoryIssue(path, "unsupported or missing Clann schema")
    if not isinstance(document.get("id"), str) or not document["id"].strip():
        return None, ClannDirectoryIssue(path, "missing Clann ID")
    if not isinstance(document.get("name"), str) or not document["name"].strip():
        return None, ClannDirectoryIssue(path, "missing Clann name")
    people = document.get("people")
    if not isinstance(people, list):
        return None, ClannDirectoryIssue(path, "missing people list")
    metadata = document.get("metadata")
    if metadata is not None and not isinstance(metadata, dict):
        return None, ClannDirectoryIssue(path, "invalid metadata")
    metadata = metadata or {}
    return (
        ClannSummary(
            path,
            document["name"].strip(),
            str(metadata.get("status", "unknown")),
            len(people),
            _stringOrNone(metadata.get("modified")),
        ),
        None,
    )


def _stringOrNone(value: Any) -> str | None:
    return value if isinstance(value, str) else None
