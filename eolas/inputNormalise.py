"""Field-aware normalisation for human-entered Eolas text."""

from typing import Any, Mapping


def codeNormalise(value: str) -> str:
    """Uppercase an all-lowercase or all-uppercase code without touching mixed case."""
    return _caseNormalise(value, style="code")


def sentenceNormalise(value: str) -> str:
    """Sentence-case unambiguous all-lowercase or all-uppercase prose."""
    return _caseNormalise(value, style="sentence")


def titleNormalise(value: str) -> str:
    """Title-case unambiguous all-lowercase or all-uppercase names and labels."""
    return _caseNormalise(value, style="title")


def controlledValueNormalise(value: Any, values: Mapping[str, str]) -> Any:
    """Match a user-entered controlled value without changing unknown text."""
    if not isinstance(value, str):
        return value
    return values.get(value.strip().casefold(), value.strip())


def _caseNormalise(value: str, *, style: str) -> str:
    text = value.strip()
    letters = [character for character in text if character.isalpha()]
    if not letters or not (
        all(character.islower() for character in letters)
        or all(character.isupper() for character in letters)
    ):
        return text
    if style == "code":
        return text.upper()
    if style == "sentence":
        return text.lower().capitalize()
    return text.title()
