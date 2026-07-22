# Domain model

The domain model describes the real-world concepts familyHandbook organises and
how they relate. It is not a database schema, file format, API design or
application architecture.

The model gives handbook chapters, emergency summaries, fictional examples,
printed output and any future software a shared language. Each output is a
projection: it selects and presents relevant parts of the same model for a
particular person and situation.

## Model principles

- Model family life, not the current folder structure or a future interface.
- A household is a planning context, not necessarily a family, couple or shared
  address.
- Record only what has a clear purpose.
- References to protected information are often safer than copies.
- Every information-bearing concept can carry a classification and review
  information.
- Jurisdiction-specific terms extend the model; they do not define its core.
- The model remains understandable and useful on paper.

## Core concepts

```text
Household
├── People
├── Properties
├── Documents
├── Assets
├── Accounts
├── Contacts
├── Wishes
└── Reviews
```

These branches are navigation aids, not isolated containers. A document can
relate to a person, property, asset or account. A contact can support several
people or responsibilities. A review can cover the whole household or selected
items.

The relationship diagram is maintained as
[Mermaid source](domainModel.mmd).

## Household

The context whose practical knowledge is being organised. A household may be
one person, people who live together, or people who coordinate responsibilities
across different homes.

Candidate information:

- display name or neutral label;
- people associated with the household;
- important locations;
- review schedule;
- trusted-reader arrangements; and
- jurisdiction profiles used by relevant guidance.

A household label should not require a legal family name or precise address.

## Person

An individual who belongs to, depends on, supports or has a responsibility in
relation to the household.

Candidate information:

- name or preferred label;
- relationship to the household or another person;
- safe contact references;
- care or medical information needed for a stated purpose;
- roles and responsibilities;
- related documents;
- emergency contacts; and
- wishes relevant to that person.

Relationships must support households that are not based on marriage, biology
or one address. Medical details are `Confidential` by default; a public template
must never contain real values.

## Property

A home, building, land, vehicle or other place-related responsibility the
household may need to operate, protect or maintain.

Candidate information:

- descriptive label rather than an unnecessary precise address;
- relationship to the household, such as home, rented property or storage;
- utilities and maintenance responsibilities;
- access and safety instructions;
- related contacts, documents, accounts and assets; and
- review information.

Security-system details, key locations and precise access instructions may be
`Confidential`. Codes and PINs are `Highly Confidential` and must not be stored
in ordinary handbook content.

## Document

A record that exists elsewhere and may be needed as evidence, authority or
guidance. The handbook normally stores a reference to it, not the document
itself.

Candidate information:

- title or descriptive label;
- document type;
- safe location reference;
- classification;
- owner or responsible person;
- related people, properties, assets or accounts;
- issuer or relevant contact;
- effective or expiry date, when useful;
- last reviewed date; and
- action needed.

Examples include a will, insurance policy, power of attorney, tenancy agreement
or care plan. A location reference must be only as precise as authorised readers
need.

## Asset

Something of practical or financial value that the household may need to
identify, protect, maintain or deal with.

Candidate information:

- descriptive label and category;
- owner or interested people;
- location reference;
- related documents, accounts, properties and contacts;
- maintenance or action information; and
- classification and review date.

The model does not require a full inventory or valuation. Include detail only
when it supports a defined handbook need.

## Account

A relationship with an organisation or service that may require attention. It
is not a container for credentials.

Candidate information:

- provider or organisation;
- purpose and account category;
- safe reference or masked identifier, only when needed;
- responsible people;
- related assets, properties, documents and contacts;
- actions that may be needed; and
- classification and review date.

Passwords, PINs, recovery codes, full payment-card details and equivalent
secrets are never account attributes in ordinary handbook content.

## Contact

A person, organisation, team or professional service that may need to be
contacted or may be able to help.

Candidate information:

- name or organisation label;
- role or reason for contact;
- preferred contact method;
- availability or escalation guidance;
- people, properties, documents, accounts or wishes supported; and
- classification and review date.

Contact does not imply legal authority. Roles such as attorney, executor and
next of kin must retain the distinctions in the [glossary](glossary.md).

## Wish

A preference, request or intention a person wants trusted readers to understand.
A wish is not automatically legally binding and must not be presented as a
substitute for a formal document.

Candidate information:

- subject and plain-language description;
- person expressing the wish;
- people who should know;
- related documents and contacts;
- whether professional or formal action is needed;
- classification; and
- review date.

## Review

Evidence that household information, selected concepts or references were
checked at a point in time.

Candidate information:

- review date;
- scope or items reviewed;
- responsible role or person;
- changes identified;
- follow-up actions and target dates; and
- next review trigger or date.

A review records that something was checked; it does not silently overwrite the
history of a requirement, ADR or legal document.

## Shared supporting concepts

The first model may also need small supporting concepts rather than repeating
free text:

- **Role:** a responsibility or authority held by a person or contact, such as
  carer, executor or attorney.
- **Relationship:** how two concepts are connected, with wording that does not
  assume a particular family structure.
- **Location reference:** a safe description of where an item or protected
  record can be found.
- **Action:** something that needs to be done, by whom and when.
- **Classification:** the handling level defined by the
  [information classification model](informationClassification.md).
- **Review information:** when an item was checked and when or why it should be
  checked again.

These are conceptual tools, not commitments to software classes or database
tables.

## Projections

```text
                         ┌───────────────────┐
                         │ Shared domain     │
                         │ model             │
                         └─────────┬─────────┘
             ┌────────────────────┼────────────────────┐
             │                    │                    │
     ┌───────▼────────┐   ┌───────▼────────┐   ┌──────▼─────────┐
     │ Handbook       │   │ Emergency      │   │ Annual review  │
     │ chapters       │   │ summary        │   │ checklist      │
     └────────────────┘   └────────────────┘   └────────────────┘
             │                    │                    │
     ┌───────▼────────┐   ┌───────▼────────┐   ┌──────▼─────────┐
     │ Printed        │   │ Fictional      │   │ Future         │
     │ handbook       │   │ example        │   │ software       │
     └────────────────┘   └────────────────┘   └────────────────┘
```

For example, an emergency summary may project urgent contacts, care needs,
property access guidance and document references. It should not create separate
copies that can drift away from the same concepts in the full handbook.

## Boundaries and open questions

This first model intentionally does not settle:

- which concepts become standalone records versus embedded content;
- the canonical YAML, Markdown or other source format;
- identifiers and versioning for private household records;
- whether organisations need a separate concept from contacts;
- how shared or conflicting wishes are represented;
- how jurisdiction-specific extensions are packaged; or
- how future software stores, queries or synchronises information.

Those choices require evidence, requirements and ADRs. They must not be inferred
from the illustrative candidate information in this document.
