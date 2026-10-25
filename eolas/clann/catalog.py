"""Discover existing Clanns for presentation and selection workflows."""

from dataclasses import dataclass
from pathlib import Path
from typing import List

import yaml

from eolas.paths import dataRootGet


@dataclass(frozen=True)
class ClannSummary:
    """Safe summary information for one local Clann."""

    name: str
    path: Path


def clannsDiscover(dataRoot: Path | None = None) -> List[ClannSummary]:
    """Return valid local Clanns without exposing private detail fields."""

    root = (dataRoot or dataRootGet()).expanduser().resolve() / "clanns"
    if not root.is_dir():
        return []

    clanns: List[ClannSummary] = []
    for path in sorted(candidate for candidate in root.iterdir() if candidate.is_dir()):
        indexPath = path / "clann.yaml"
        if not indexPath.is_file():
            continue
        try:
            document = yaml.safe_load(indexPath.read_text(encoding="utf-8"))
        except (OSError, yaml.YAMLError):
            continue
        if not isinstance(document, dict):
            continue
        name = document.get("name")
        if not isinstance(name, str) or not name.strip():
            continue
        clanns.append(ClannSummary(name=name.strip(), path=path))
    return clanns
