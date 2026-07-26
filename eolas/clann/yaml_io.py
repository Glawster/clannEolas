"""Reusable safe YAML file output."""

from pathlib import Path
from typing import Any, Mapping

import yaml


def yamlWrite(path: Path, document: Mapping[str, Any]) -> None:
    """Write a plain, ordered YAML mapping with a final newline."""

    content = yaml.safe_dump(
        dict(document),
        allow_unicode=True,
        default_flow_style=False,
        sort_keys=False,
    )
    path.write_text(content.rstrip("\n") + "\n", encoding="utf-8")
