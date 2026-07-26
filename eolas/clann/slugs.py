"""Safe, deterministic slug generation."""

import re
import unicodedata
from typing import Iterable, List, Set


def slugCreate(value: str) -> str:
    """Convert text into a safe non-empty ASCII path slug."""

    normalized = unicodedata.normalize("NFKD", value)
    asciiValue = normalized.encode("ascii", "ignore").decode("ascii").lower()
    slug = re.sub(r"[^a-z0-9]+", "-", asciiValue)
    slug = re.sub(r"-+", "-", slug).strip("-")
    if not slug:
        raise ValueError("A slug cannot be generated from an empty value.")
    return slug


def slugsCreateUnique(values: Iterable[str]) -> List[str]:
    """Create deterministic unique slugs using numeric duplicate suffixes."""

    used: Set[str] = set()
    result: List[str] = []

    for value in values:
        baseSlug = slugCreate(value)
        candidate = baseSlug
        suffix = 2
        while candidate in used:
            candidate = f"{baseSlug}-{suffix}"
            suffix += 1
        used.add(candidate)
        result.append(candidate)

    return result
