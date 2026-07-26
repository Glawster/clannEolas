"""Replaceable parsing for simple Western-style full names."""

from dataclasses import dataclass
from typing import List, Optional


@dataclass(frozen=True)
class ParsedName:
    """Structured components parsed from a full name."""

    first_name: str
    middle_names: List[str]
    last_name: Optional[str]


def nameParse(fullName: str) -> ParsedName:
    """Parse the first, middle, and last tokens of a non-empty name."""

    tokens = fullName.split()
    if not tokens:
        raise ValueError("Full name cannot be empty.")
    if len(tokens) == 1:
        return ParsedName(
            first_name=tokens[0],
            middle_names=[],
            last_name=None,
        )
    return ParsedName(
        first_name=tokens[0],
        middle_names=tokens[1:-1],
        last_name=tokens[-1],
    )
