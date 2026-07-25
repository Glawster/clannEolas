# Household bootstrap wizard

The household bootstrap wizard creates the initial private YAML data structure
for an Eolas household.

## Run the wizard

From the repository root, install the Python dependency and run:

```bash
python -m pip install -r requirements.txt
python -m eolas ask-household
```

The wizard asks for:

1. The household name and output directory.
2. The number of people in the household.
3. Each person's full name, preferred name, household role and adult status.
4. The primary person or record owner.
5. Confirmation after displaying the target path and a summary.

Suggested roles are `self`, `spouse`, `partner`, `child`, `parent`, `relative`
and `other`, but custom roles are accepted. The default final confirmation is
yes. Pass `--confirm` to generate after showing the summary without the final
question.

The command refuses to overwrite a non-empty household directory. It builds
the entire structure in a temporary directory and publishes it only when every
file has been written successfully.

## Generated structure

For a household called `Example Household`, the initial structure resembles:

```text
example-household/
├── household.yaml
├── people/
│   ├── alex-example/
│   │   ├── person.yaml
│   │   └── identity.yaml
│   └── sam-example/
│       ├── person.yaml
│       └── identity.yaml
├── addresses/
├── properties/
├── vehicles/
├── finances/
├── contacts/
├── documents/
└── backups/
```

The identity files contain sensitive personal-data placeholders. Store live
household data in an appropriately protected location and never commit it to a
public source repository.

## Reuse from Python or Qt

The questionnaire is separate from household generation. A future Qt setup
wizard, importer or test can construct typed inputs and call the service
without using console input:

```python
from pathlib import Path

from eolas import HouseholdInput, PersonInput, householdCreate

household = HouseholdInput(
    name="Example Household",
    members=[
        PersonInput(
            full_name="Alex Example",
            preferred_name="Alex",
            household_role="self",
            is_adult=True,
            is_primary=True,
        )
    ],
)

createdPath = householdCreate(household, Path("/private/eolas-data"))
```

`householdCreate()` validates the model, creates stable IDs, writes the
directory tree atomically and returns the new household path. It does not call
`input()` or print to the console.
