"""Central definitions for a Clann data tree."""

from typing import Dict, Tuple

PERSON_SECTIONS: Dict[str, Dict[str, str]] = {
    "identity": {
        "filename": "identity.yaml",
        "schema": "eolas/person/identity/v1",
    }
}

CLANN_DIRECTORIES: Tuple[str, ...] = (
    "people",
    "households",
    "relationships",
    "contacts",
    "professionals",
    "documents",
    "shared",
)

