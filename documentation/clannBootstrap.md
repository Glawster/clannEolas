# Clann bootstrap wizard

The bootstrap wizard creates a Clann, its primary household, and the first
people represented by Eolas.

## Run the wizard

```bash
python -m pip install -r requirements.txt
python3 -m eolas clann --create
```

The wizard asks for the Clann name, primary household, current residents,
primary person, and any Clann people who live elsewhere. Pass `--confirm` to
generate after showing the summary without the final confirmation.

Private Eolas data is always rooted at `~/eolas`. A Clann named `Example
Clann` is therefore written beneath `~/eolas/clanns/example-clann/`. Creation
is atomic and refuses to overwrite a non-empty Clann directory.

## Generated structure

```text
~/eolas/
└── clanns/
    └── example-clann/
        ├── clann.yaml
        ├── people/
        │   └── alex-example/
        │       ├── person.yaml
        │       └── identity.yaml
        ├── households/
        │   └── family-home/
        │       └── household.yaml
        ├── relationships/
        ├── contacts/
        ├── professionals/
        ├── documents/
        └── shared/
```

`clann.yaml` indexes all people and households. Household records contain
residence memberships; person records refer to the Clann and repeat their
household memberships for convenient lookup. A person who lives elsewhere
still belongs to the Clann and can have an empty membership list until their
household is recorded.

Contacts and professionals are deliberately separate from Clann people.
Relationships are also independent of residence.

## Reuse from Python or Qt

```python
from pathlib import Path

from eolas import ClannInput, PersonInput, clannCreate

clann = ClannInput(
    name="Example Clann",
    primary_household_name="Family Home",
    people=[
        PersonInput(
            full_name="Alex Example",
            preferred_name="Alex",
            household_role="householder",
            is_adult=True,
            is_primary=True,
        )
    ],
)

createdPath = clannCreate(clann, Path.home() / "eolas")
```

The identity files contain sensitive personal-data placeholders. Store live
data in an appropriately protected location and never commit it publicly.
