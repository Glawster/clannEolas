"""Central definitions for the initial household data structure."""

from typing import Dict, Tuple

PERSON_SECTIONS: Dict[str, Dict[str, str]] = {
    "identity": {
        "filename": "identity.yaml",
        "schema": "eolas/person/identity/v1",
    }
}

HOUSEHOLD_DIRECTORIES: Tuple[str, ...] = (
    "addresses",
    "properties",
    "vehicles",
    "finances",
    "contacts",
    "documents",
    "backups",
)
