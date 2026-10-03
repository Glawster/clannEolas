"""Shared Eolas application paths."""

from pathlib import Path


def dataRootGet() -> Path:
    """Return the private Eolas data root for the current user.

    This preserves the currently implemented storage location while keeping
    presentation layers independent of one another.
    """

    return Path.home() / "eolas"
