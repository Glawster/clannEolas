# 009: Banking module

Priority: high  
Owner: project maintainers

## Status

ToDo

## Outcome

As a person preparing a Clann record, I need to describe the household's banking
relationships, money movements, authorities and continuity arrangements so that
an authorised helper can understand what exists and protect essential finances
without needing account credentials.

As an executor, administrator, attorney, deputy or surviving account holder, I
need reliable, current and appropriately classified banking information so that
I can identify institutions, establish my authority, preserve essential income
and payments, and keep an evidence-based record of actions during a stressful
transition.

## Context

Banking continuity is broader than a list of balances. A household may depend on
several sole, joint, trust, children's, business, credit and savings
relationships. Money arrives and leaves through mechanisms with different
owners, mandates and cancellation effects. A death, loss of capacity, hospital
stay or overseas emergency may change who is legally authorised to act while
essential bills continue to fall due.

Eolas must help a trusted person answer five questions:

1. Which banking relationships exist, and who owns or controls each one?
2. Which essential commitments and income streams depend on them?
3. Which documents, authorities, contacts and physical items are needed?
4. What should be checked or escalated in this particular event and
   jurisdiction?
5. What was decided, by whom, on what authority and using which evidence?

The module must support preparation and continuity without becoming an online-
banking client, credential store, financial ledger or source of personalised
legal or financial advice. It models banking knowledge in the shared Eolas
domain and projects that knowledge into reports and event-specific checklists.

This specification is initially UK-oriented. Legal authority, succession,
probate terminology, deposit protection and institution processes vary by
jurisdiction and over time. Eolas must separate durable facts from dated
guidance, identify the applicable jurisdiction and direct users to the relevant
institution or official source for current requirements.

## Domain principles

1. **Continuity before completeness.** Capture enough to find the relationship,
   understand dependencies and take the next authorised action. Do not request
   sensitive detail merely because it appears on a statement.
2. **Authority is explicit.** Ownership, beneficial interest, signing mandate,
   attorney authority, deputyship and executor authority are different facts.
   One must never be inferred from another.
3. **Accounts are not credentials.** A banking relationship may record a safe
   identifier and access arrangements, but never a password, PIN, passcode,
   security answer, one-time code, recovery code or card verification value.
4. **Relationships are first-class.** Accounts connect people, institutions,
   cards, income, payment commitments, liabilities, documents and instructions.
   These concepts must not be duplicated as unconnected prose.
5. **The underlying obligation matters.** Cancelling a Direct Debit, standing
   order, card authority or payment permission does not necessarily cancel the
   contract or debt it pays. Eolas must keep payment method and obligation
   separate.
6. **No unauthorised access.** Knowledge of credentials or possession of a card
   does not confer authority. Guidance must direct users to the institution and
   the appropriate legal route.
7. **Actions are contextual.** A sensible action after death may be harmful
   during temporary illness. Recommendations must be event-specific, reviewable
   and clearly distinguished from confirmed institution instructions.
8. **Evidence and time matter.** Balances, rates, contacts and procedures become
   stale. Records must show source, effective date, review date and uncertainty.
9. **Privacy defaults upward.** Identifiers are masked in ordinary views and
   reports; missing classification fails closed as `highlyConfidential`.
10. **Jurisdiction-neutral core.** UK terminology and guidance extend shared
    concepts rather than defining the core account model.

## Actors and roles

| Role | Banking concern | Boundary Eolas must preserve |
| --- | --- | --- |
| Account holder | Understand and maintain their own relationships | Capacity and ownership are not inferred from ordinary access |
| Joint holder | Continue shared finances and understand liabilities | Joint access does not prove beneficial ownership or authority over sole accounts |
| Trusted helper | Assist with practical administration | Help does not itself grant transaction authority |
| Attorney | Act within a valid power and its restrictions | Authority, activation conditions and jurisdiction must be verified |
| Deputy or guardian | Act under a court order | Powers are limited to the order and applicable law |
| Executor or administrator | Identify, value and administer estate banking | Authority begins and is evidenced differently across jurisdictions and estates |
| Trustee | Administer money for beneficiaries under a trust | Legal title, beneficial interest and trust terms remain distinct |
| Parent or guardian | Support a child's banking | Account ownership and withdrawal rights depend on product terms and age |
| Business officer or partner | Maintain business banking | Personal Clann role does not confer business authority |
| Financial adviser or accountant | Provide professional support | Advice and professional access do not imply ownership or transaction authority |
| Institution contact | Operate the provider's process | Contact status does not imply legal authority within the Clann |

## Information priority

Field priority describes the requirement to model and prompt for information;
it does not make every value applicable to every account.

- **Mandatory:** required to create a usable record when applicable. If unknown,
  record `unknown` with a follow-up action rather than inventing a value.
- **Recommended:** expected when available because it materially improves
  continuity, verification or review.
- **Optional:** collect only for a stated purpose chosen by the user.
- **Never store:** prohibited in Eolas regardless of convenience.
- **Future:** reserved for a later approved capability and not required by the
  initial module.

## Banking relationship coverage

### Supported relationship categories

The domain must represent at least:

| Category | Continuity significance |
| --- | --- |
| Current or transaction account | Common source of essential income, bills, cards and cash access |
| Savings or deposit account | May hold reserves, estate value or emergency funds with withdrawal conditions |
| Joint account | May continue for survivors but needs mandate, contribution and beneficial-interest context |
| Children's or junior account | Adult control, beneficial ownership and control-at-age rules may differ |
| Building society account | May use passbooks, branch processes or membership rights |
| Credit card or charge card | Represents credit and recurring card authorities, not a deposit balance |
| Cash ISA | Has tax-wrapper and transfer considerations distinct from an ordinary savings account |
| Notice or fixed-term deposit | Access may be delayed, penalised or limited until maturity |
| Foreign-currency account | Currency, conversion, correspondent and cross-border considerations apply |
| Business, partnership or charity account | Authority and continuity follow organisational mandates, not family relationships |
| Trust, client or nominee account | Legal holder, beneficial owner, trustee powers and segregation must be explicit |
| Online-only or app-based bank | Access and support may depend on a device, app and recovery channel rather than a branch |
| Basic bank account | Essential transaction service may have product-specific limits and no overdraft |
| Offset, linked or packaged account | Balance or fee may affect a mortgage, insurance, benefit or another product |
| Dormant, restricted or closed account | Funds or evidence may remain relevant even without current activity |

Credit cards share institutions, statements, payments and continuity workflows
with bank accounts but must retain their nature as revolving credit. Mortgages,
loans, investments, insurance and pensions are linked products owned by their
respective future modules rather than subtypes of bank account.

## Functional requirements

### BR-1: Institution records

Institutions must be reusable entities rather than repeated text on each
account. Trading brand, legal entity and banking licence group must be capable
of being represented separately because service contacts and deposit-protection
aggregation may differ.

| Information | Priority | Why it matters |
| --- | --- | --- |
| Institution display name | Mandatory | Identifies whom the relationship is with |
| Legal entity or authorised firm | Recommended | Supports formal correspondence and protection checks |
| Trading brand | Recommended | Matches statements and the name familiar to the household |
| Institution type | Recommended | Distinguishes bank, building society, credit union, card issuer or e-money provider |
| Country and regulatory jurisdiction | Recommended | Determines rules, protection and escalation routes |
| Current official website | Recommended | Provides a starting point that can be independently verified |
| General contact channels | Recommended | Supports routine administration without relying on one channel |
| Bereavement or deceased-estates team | Recommended | Reduces delay after death |
| Attorney/deputy support route | Recommended | Helps register or use authority during incapacity |
| Fraud and lost-card route | Recommended | Supports urgent protective action |
| Accessibility or vulnerability support | Optional | Records an established support route or communication need |
| Branch name and safe location | Optional | Useful for passbook, identity, cash or in-person processes |
| Relationship manager or business team | Optional | Useful where the institution assigns a durable role; personal details need review |
| Banking licence or protection group | Recommended for UK deposits | Prevents treating separate brands as separate protection limits |
| Source and last-verified date | Mandatory for operational contacts | Reveals staleness and supports re-verification |

Eolas must allow a contact route to be marked as institution-confirmed,
official-source-derived, user-provided or unverified. It must never present an
old telephone number or URL as current merely because it is stored. Before an
urgent or sensitive contact, guidance must advise independent verification from
an official source to reduce phishing risk.

### BR-2: Account identity and purpose

Each account record must support:

| Information | Priority | Handling and rationale |
| --- | --- | --- |
| Stable Eolas account ID | Mandatory | Internal identity independent of provider identifiers |
| Account category and product name | Mandatory | Explains function, access rules and linked workflows |
| User-chosen nickname | Recommended | Gives trusted readers a recognisable, non-sensitive label |
| Purpose | Mandatory | Identifies household bills, emergency reserve, tax, child savings or another role |
| Institution link | Mandatory | Connects the account to reusable contacts and licence information |
| Status | Mandatory | At least active, dormant, restricted, closure pending, closed or unknown |
| Opened and closed dates | Optional | Supports history, dormancy and audit |
| Servicing channel | Recommended | Branch, telephone, postal, web, app-only or mixed |
| Primary country, currency and time zone | Recommended | Prevents amount, deadline and contact ambiguity |
| Statement frequency and delivery method | Recommended | Helps find evidence and detect missing statements |
| Last confirmed date and source | Mandatory | Shows whether the relationship is current |
| Notes limited to continuity purpose | Optional | Must be classified and must reject prohibited secrets |

### BR-3: Account identifiers

Identifiers must be separate typed fields with country and format context. Eolas
must support masking, field-level classification and purpose-based access.

| Identifier | Priority | Requirement |
| --- | --- | --- |
| Masked account number or provider reference | Recommended | Default continuity identifier; show only sufficient trailing characters |
| Sort code or domestic routing code | Optional | Useful for UK account verification and payments; confidential with account identifier |
| Full account number | Optional | Store only after explaining a concrete need and safer-reference alternative |
| IBAN | Optional | Useful for international identification; validate format, not ownership |
| SWIFT/BIC | Optional | Identifies an institution/branch for international transfers; may be derived and must retain source |
| Customer or membership number | Optional | May help institution lookup but may also form part of authentication; masked by default |
| Roll number or building-society reference | Optional | May be required where sort code/account number alone is insufficient |
| Credit-card account reference | Recommended if present | Must not be confused with or derived from the full card PAN |
| External product ID | Optional | Supports a provider-specific product where it has continuity value |

The full primary account number, IBAN, sort code plus account number, and
customer number are at least `Confidential`. A value used by an institution as
an authentication secret is `Highly Confidential` and prohibited from ordinary
Eolas storage even if it is also labelled an account reference.

### BR-4: Ownership, interest and authority

The model must represent, independently:

- legal account holders and the dates of their association;
- beneficial owners and documented proportions where known;
- sole or joint ownership and number of holders;
- joint signing rule, such as either-to-sign or all-to-sign, where confirmed;
- contributions or source-of-funds notes when needed to understand beneficial
  interest, without attempting a complete accounting;
- trustees, beneficiaries, nominees and the governing document reference;
- parental or guardian control and the child beneficial owner;
- attorneys, deputies, guardians or authorised third parties;
- business owners, partners, directors, officers and mandate signatories;
- additional cardholders, who are not thereby account owners;
- authority start and end dates, activation conditions, restrictions and
  current verification status; and
- evidence for each non-owner authority, such as an LPA, court order, mandate or
  institution confirmation.

The record must distinguish `has authority`, `authority expected but not
registered`, `registration in progress`, `authority restricted`, `authority
ended` and `unknown`. Eolas must not infer a right to transact from relationship,
co-residence, next-of-kin status, possession of a device or prior informal help.

Joint account continuity varies with product terms, mandate, beneficial
ownership, incapacity and jurisdiction. UK consumer guidance says a joint
account will normally continue in the remaining names after a death, while an
institution may restrict a joint account after a holder loses capacity until
valid authority is established. Eolas must present these as review prompts,
not universal outcomes. See [MoneyHelper joint-account guidance](https://www.moneyhelper.org.uk/en/everyday-money/banking/joint-accounts)
and [Office of the Public Guardian guidance for managing another person's bank
account](https://www.gov.uk/government/publications/deputy-and-attorney-guidance-dealing-with-banks).

### BR-5: Balance, terms and protection context

Eolas is not a live balance service in the initial module. It may retain a
point-in-time balance only with currency, `asOf` time, source and an explicit
warning that the value may have changed.

The account must support recommended continuity facts:

- whether it normally carries a positive balance, overdraft or credit debt;
- arranged overdraft existence, limit and review date without inferring
  available funds;
- minimum balance, notice period, withdrawal restriction, maturity date and
  early-access consequence where applicable;
- interest and fee review references rather than rapidly stale copied rates;
- protection-scheme name, eligibility status (`confirmed`, `likely`, `not
  covered`, `unknown`) and verification date;
- authorised-firm or licence-group link used for aggregation; and
- a temporary-high-balance event, its source, qualifying-date estimate and
  review action where relevant.

Protection values must come from dated, updateable jurisdiction guidance rather
than a permanent field default. As of 2026-07-31, the UK FSCS states that
eligible deposits are protected up to GBP 120,000 per eligible person per
authorised firm, aggregated across brands sharing a banking licence; qualifying
temporary high balances may receive additional time-limited protection. Eolas
must link to and encourage checking the [current FSCS rules](https://protected.fscs.org.uk/what-we-cover/banks-building-societies-credit-unions/deposit-limit-increase/)
rather than treating these figures as timeless or guaranteeing eligibility.

### BR-6: Outgoing commitments

Payments must be reusable records linked separately to the funding account and
the underlying provider, contract, liability or internal destination.

Supported mechanisms must include Direct Debit, standing order, scheduled bank
transfer, internal transfer, recurring card payment/continuous payment
authority, cheque, manual bank transfer and Variable Recurring Payment or other
Open Banking payment permission.

| Information | Priority | Purpose |
| --- | --- | --- |
| Payment mechanism | Mandatory | Determines control, visibility and cancellation route |
| Plain-language purpose | Mandatory | Lets a helper understand what continuity depends on it |
| Payee/provider link | Mandatory | Identifies whom to contact and the underlying relationship |
| Funding account or card link | Mandatory | Reveals what may fail if an account or card is restricted |
| Provider/customer reference | Recommended | Helps the provider locate the obligation; masked where needed |
| Frequency or schedule | Mandatory | Supports cash-flow and deadline review |
| Typical, fixed or last amount and currency | Recommended | Indicates scale but must state which kind of amount and effective date |
| Variability and known range | Recommended | Prevents a last payment being mistaken for a fixed commitment |
| Next known due date | Optional | Useful but time-sensitive and must carry source date |
| Start/end date | Optional | Helps identify stale or fixed-term arrangements |
| Essentiality and consequence of failure | Mandatory | Prioritises housing, utilities, care, insurance, tax and debt payments |
| Contract or liability link | Recommended | Ensures mandate cancellation is not mistaken for contract cancellation |
| Responsible reviewer and review interval | Recommended | Establishes ownership for periodic checks |
| Event-specific action | Recommended | Captures `continue`, `contact provider`, `change payer`, `pause if authorised`, `cancel if authorised`, `settle`, `unknown` |
| Action source and status | Mandatory when an action is stated | Distinguishes a household preference from provider-confirmed instruction |

Event-specific actions must be separately recordable for death, loss of
capacity, temporary illness/hospitalisation, overseas emergency, relationship
breakdown and moving home. A generic recommendation must not overwrite a
provider-confirmed instruction.

Eolas must explain that Direct Debits, standing orders and recurring card
payments are different instructions and that stopping any of them does not
necessarily end the debt or service. This distinction is supported by
[MoneyHelper's current payment guidance](https://www.moneyhelper.org.uk/en/everyday-money/banking/direct-debits-and-standing-orders.html).

For Variable Recurring Payments, the model must support the authorised payment
provider, source and destination accounts, purpose, permission start/end,
per-payment and period limits, frequency constraints, consent status and review
route. It must not imply universal bank or merchant availability. Open Banking
describes these as long-lived permissions within agreed limits; current scope
continues to evolve, so Eolas must reference [current Open Banking
guidance](https://www.openbanking.org.uk/variable-recurring-payments-vrps/).

### BR-7: Incoming payments

The module must represent salary, occupational and state pension, benefits,
dividends, interest, rent, maintenance, child support, trust distributions,
investment income, business drawings, refunds and other recurring or material
incoming payments.

Each incoming payment must support:

- payer or source and plain-language purpose (**Mandatory**);
- receiving account (**Mandatory**);
- recipient or beneficial owner (**Mandatory**);
- frequency or trigger (**Mandatory**);
- typical or last amount, currency and effective date (**Recommended**);
- payer reference, employee/payroll reference or claim reference
  (**Optional**, masked and classified);
- whether another household obligation depends on the income (**Recommended**);
- taxation or adviser reference without giving tax advice (**Optional**);
- expected behaviour after death, incapacity, hospitalisation or change of
  address (**Recommended**); and
- contact, notification action, evidence source and review date
  (**Recommended**).

Continuity reporting must highlight income paid into an account likely to be
restricted and outgoing essentials that rely on it. It must not assume an
income continues after death or incapacity; the responsible payer must confirm
entitlement, overpayment and redirection rules. Government notification
services do not notify every private bank, pension or payer, as reflected in
[GOV.UK Tell Us Once guidance](https://www.gov.uk/after-a-death/organisations-you-need-to-contact-and-tell-us-once).

### BR-8: Linked products and dependencies

An account must link to, rather than duplicate:

- mortgage and secured-loan payment or offset arrangements;
- personal, vehicle, student, business and other loan repayments;
- overdraft facilities and related debt;
- savings, investments, pensions and cash-management platforms;
- insurance premiums, packaged-account benefits and eligibility conditions;
- credit cards and their repayment accounts;
- utilities, council tax, rent, service charges and household contracts;
- payroll, benefits, pensions, rental and investment income;
- safe-deposit, currency, merchant, payment and cash-management services; and
- documents, statements, tax records and professional contacts.

Each link must state relationship type, direction, effective dates, source and
review status. Closing or changing an account must trigger a dependency review,
not cascade-delete the linked records. A relationship that affects pricing,
cover, eligibility, offset interest or access must be prominently classed as a
continuity dependency.

### BR-9: Cards and payment instruments

The module must support debit, credit, charge, cash, prepaid, virtual and
additional-holder cards as instruments linked to an account or facility.

| Information | Priority | Requirement |
| --- | --- | --- |
| Card type and issuer | Mandatory | Distinguishes instrument and responsible institution |
| Linked account/facility | Mandatory | Shows funding or debt relationship |
| Named holder/additional holder | Mandatory | Does not imply account ownership |
| Masked last four digits | Recommended | Supports identification without retaining full PAN |
| Expiry month/year | Optional | Helps identify replacement and stale subscriptions |
| Physical/virtual status | Recommended | Guides location and device continuity |
| Active, frozen, replaced, lost, expired or cancelled status | Mandatory | Prevents reliance on an invalid instrument |
| Replacement relationship | Recommended | Preserves history and recurring-payment review |
| Safe physical location reference | Optional | Useful for recovery; classification may need to be `Confidential` |
| Lost/stolen contact route | Recommended | Supports urgent action after independent verification |
| Recurring-payment links | Recommended | Identifies services affected by replacement or cancellation |

Eolas must never store a full primary account number (PAN) for a payment card,
PIN, CVV/CVC, magnetic-stripe or chip data, one-time passcode, app approval
secret or card security answer. It must not encourage a survivor or
representative to use the deceased or donor's card or credentials.

### BR-10: Banking equipment and physical evidence

The module must represent an inventory/reference for cheque books, paying-in
books, passbooks, card readers, hardware security keys, authentication devices,
bank-issued tokens and relevant safe-deposit access items.

Each item must support type, institution/account links, custodian, status,
issued/replaced date, safe location reference, return or destruction
instruction, event-specific relevance, classification and review date.

Serial numbers are optional and must be stored only when the institution uses
them for inventory rather than authentication. Activation codes, generated
codes, seed values and device unlock secrets are never stored. Location detail
must be no more precise than the authorised reader needs.

### BR-11: Online and telephone banking arrangements

Safe continuity information may include:

- available channels: website, app, telephone, branch, post or accessible
  alternative (**Recommended**);
- official service URL or app name, independently verifiable (**Recommended**);
- authentication method categories such as password, app approval, biometric,
  SMS, hardware token or card reader (**Recommended**);
- the owner and safe location reference for the enrolled phone, email address,
  SIM, card reader or security key (**Optional**);
- password-manager or digital-estate-plan reference, without the password or
  recovery material (**Optional**);
- provider recovery and accessibility route (**Recommended**);
- whether an attorney, delegate or business user has a separately issued login
  (**Recommended where applicable**); and
- last successful owner verification date, without recording access-event
  details (**Optional**).

Eolas must not test credentials, log in to online banking, store session tokens,
automate authentication or present another person's recovery channel as a route
for bypassing provider controls. Biometrics belong to a person and device; they
must not be described as transferable continuity credentials.

### BR-12: Statements and evidence

Statements may support account discovery, masked identifier verification,
balance evidence, transaction history, recurring-payment and income discovery,
estate valuation, tax work and reconciliation.

The account record must support statement period, issue date, document/evidence
link, source, import attempt, review state and checksum/provenance through the
[Document Import Framework](008-documentImportFramework.md). It must distinguish
an original statement, downloaded copy, scan, redacted derivative and extracted
candidate data.

Statement review may propose accounts, institutions, incoming payments,
outgoing commitments and linked products. No proposal becomes canonical until
confirmed. A statement is historical evidence, not proof that a relationship
is still open, that a balance is current or that a transaction will recur.

Retention must be purpose-based. Eolas must support a safe reference instead of
a stored copy, classification, encrypted evidence storage where available,
redaction derivatives, retention review and secure-deletion limitations.

### BR-13: Reviews, reminders and data quality

Every banking relationship must support a responsible reviewer, last reviewed
date, next review date or trigger, review scope, evidence source and follow-up
actions.

Review prompts must cover:

- ownership, authority and contact changes;
- account status, purpose and stale balances;
- incoming and outgoing dependency changes;
- card replacement and orphaned recurring authorities;
- fixed-term maturity, notice and fee changes;
- protection-group and guidance changes;
- branch closure or digital-access changes;
- house move, relationship change, birth, adulthood, business-role change,
  incapacity and death; and
- unexplained activity, dormant relationships or duplicate account records.

Unknown values, contradictions and overdue reviews must remain visible. Eolas
must not manufacture completeness scores from unanswered sensitive fields.

## Continuity workflows

### Workflow rules

1. Every workflow must begin by identifying the affected person, event,
   jurisdiction, urgency and actor's claimed authority.
2. Eolas must distinguish preparation guidance, household preference,
   institution-confirmed instruction and completed action.
3. The user must be able to mark an action `notStarted`, `inProgress`, `waiting`,
   `completed`, `notApplicable` or `blocked`, with responsible person, date,
   evidence, notes and next step.
4. Guidance must never direct use of another person's credentials or assume
   that next of kin can transact.
5. Essential housing, utilities, care, food, tax, insurance and debt payments
   must be reviewed before discretionary cancellations.
6. Suspected fraud, abuse, coercion, conflict between representatives or doubt
   about authority must trigger a stop-and-escalate path to the institution and
   appropriate professional or safeguarding support.

### Death

Timing is a prioritisation aid, not a legal deadline. The institution, personal
representative and applicable jurisdiction determine the actual process.

#### First 48 hours

- Preserve records, devices, cards, statements and post without using the
  deceased person's credentials or payment instruments.
- Identify immediate cash, funeral, dependant, housing and care needs and which
  sole or joint accounts fund them.
- Record the death and responsible contacts; do not rush to close accounts or
  cancel every payment before dependencies are understood.
- If fraud or continuing unauthorised use is suspected, contact the
  institution's independently verified urgent channel.

#### First week

- Identify the executor/administrator route and obtain official death
  certificates or jurisdiction-equivalent evidence.
- Notify known institutions through their bereavement process when the
  responsible person is ready and record reference, date, requested documents
  and resulting restrictions.
- Confirm treatment of joint accounts, essential Direct Debits, standing orders,
  cards, credit balances, debts and safe-deposit arrangements with each
  institution.
- Redirect or protect essential bills and notify private income providers that
  are not covered by government notification services.
- Ask the institution whether it can pay a funeral invoice directly from the
  deceased's funds before probate; do not assume availability or withdraw funds
  using known credentials. MoneyHelper notes this may be possible subject to
  evidence and provider policy: [funeral payment guidance](https://www.moneyhelper.org.uk/en/family-and-care/death-and-bereavement/help-paying-for-a-funeral).

#### First month

- Obtain date-of-death balances, interest, debt and transaction information
  needed for estate and tax work.
- Review every incoming payment for entitlement, overpayment or redirection and
  every outgoing commitment for continuation, transfer, settlement or
  authorised cancellation.
- Identify unknown accounts from statements, tax records, post and approved
  tracing services; the UK Dormant Assets Scheme points users to My Lost
  Account for bank and building-society tracing: [GOV.UK dormant-assets
  guidance](https://www.gov.uk/government/publications/the-dormant-accounts-scheme).
- Record provider thresholds and whether probate, confirmation or another grant
  is required; these differ by provider, value and jurisdiction.
- Review joint-account beneficial ownership and contribution evidence for
  estate/tax work rather than assuming the operational survivor treatment
  settles beneficial ownership.

#### Estate administration

- Maintain an inventory of accounts, date-of-death values, post-death interest,
  liabilities, notifications, closures, transfers and retained amounts.
- Keep estate money separate from personal money and preserve a transaction and
  decision record. Official guidance for attorneys similarly stresses
  separation and records; estate-account needs remain jurisdiction- and
  provider-specific.
- Reconcile institution proceeds to estate records and investigate variances.
- Preserve statements and closure evidence for the required tax, estate and
  challenge period.
- Review eligible temporary high balances and banking-licence aggregation using
  current official protection guidance.
- Close or transfer accounts only with verified authority and after linked
  payments, income, debts, tax and product consequences are addressed.

The executor checklist must acknowledge that `Tell Us Once` notifies specified
government bodies but private financial institutions generally need separate
contact. It must not imply that a grant is always or never required.

### Loss of capacity

- Record the decision-specific capacity concern without Eolas making a medical
  or legal determination.
- Identify the applicable registered property/financial power, enduring power,
  continuing power, deputyship, guardianship or other jurisdictional authority,
  including instructions, restrictions and how multiple representatives act.
- Preserve the person's participation and preferences to the extent possible;
  do not treat diagnosis or age alone as loss of capacity.
- Register authority separately with each institution and record requested
  identity, address and authority evidence, provider reference and access method.
- Confirm treatment of joint accounts and essential payments with the provider.
- Keep the person's money separate, keep decisions and receipts, avoid conflicts
  and record the best-interests basis where applicable.
- Use a separately issued attorney/deputy access route where offered; never use
  the donor's login, card or PIN.

For England and Wales, Eolas guidance must link to current [Office of the Public
Guardian attorney/deputy banking guidance](https://www.gov.uk/government/publications/deputy-and-attorney-guidance-dealing-with-banks)
and [property and financial affairs attorney duties](https://www.gov.uk/manage-lasting-power-attorney/property-financial-affairs).
Scotland and Northern Ireland require separate jurisdiction content and must
not be relabelled as an LPA workflow.

### Prolonged hospital stay or temporary assistance

- Confirm whether the person retains capacity and can give instructions.
- Prefer institution-supported third-party mandates, delegated access,
  accessible banking or an applicable ordinary/continuing power over credential
  sharing.
- Identify essential payment and income deadlines, cash needs and accessible
  communication arrangements.
- Define the helper's permitted actions, start/end date and review trigger.
- Revoke temporary arrangements and review transactions when the person resumes
  management.
- Escalate to legal advice if capacity or authority is uncertain; informal
  family status alone is insufficient.

### Overseas emergency

- Record institution emergency numbers, country/time-zone context, travel and
  card dependencies, and an alternate safe way to meet essential costs.
- For a lost device or card, use independently verified provider channels,
  preserve incident references and review virtual cards and recurring payments.
- Do not store travel-notification answers, card security data or recovery codes.
- Confirm whether a representative's authority is recognised and usable across
  the relevant jurisdictions; do not assume a domestic power is automatically
  accepted abroad.
- Review fraud, currency, cash access, insurance and return-travel dependencies.

### Moving home

- Identify institutions, cards, statements and linked products requiring an
  address update.
- Review branch, cash, passbook and accessibility needs at the new location.
- Update payer/payee records and billing addresses through authorised channels.
- Confirm completion; do not retain superseded precise addresses longer than
  their evidence or audit purpose requires.

## Executor and representative guidance requirements

### Executor banking guide

The generated guide must help an executor or administrator:

- find every known institution and distinguish sole, joint, trust, business and
  credit relationships;
- locate the will, authority/grant evidence, death certificates, identity
  documents, statements and tax/professional contacts without exposing secrets;
- identify provider bereavement routes and independently verify them;
- record date-of-death balances, interest, liabilities, income and payments;
- understand which essential bills may fail when a sole account is restricted;
- distinguish operational treatment of a joint account from estate and tax
  beneficial-interest questions;
- determine from each provider whether a grant is required and which documents
  it accepts;
- keep an institution contact log, evidence requests, reference numbers and
  follow-ups;
- reconcile proceeds and maintain estate accounts; and
- escalate tax, foreign, trust, business, disputed-ownership, insolvency and
  contested-authority questions to an appropriate professional.

It must warn against common mistakes:

- using the deceased person's card, PIN, app or online login;
- transferring funds before authority and ownership are established;
- cancelling all regular payments without checking essential services and
  contractual obligations;
- assuming joint account access proves the survivor owns the whole balance for
  estate or tax purposes;
- assuming Tell Us Once informs private financial institutions;
- overlooking credit balances, overdrafts, packaged benefits, subscriptions,
  business accounts, foreign currency and dormant accounts;
- mixing estate and personal funds;
- trusting contact details in an unexpected message; and
- closing an account before statements, tax evidence and linked dependencies
  are secured.

### Attorney, deputy and guardian guide

The guide must identify:

- authority type, jurisdiction, registration status, activation conditions,
  restrictions and how joint representatives act;
- donor/account-holder participation, preferences and communication needs;
- institution registration status and separately issued access mechanisms;
- essential spending, income and cash-flow needs;
- conflicts, gifts, loans, unusual transactions and professional-advice flags;
- separation of funds and supporting receipts/decision records;
- review and reporting duties; and
- authority expiry, revocation, replacement and death transitions.

Eolas must not present health and welfare authority as financial authority or
an ordinary informal mandate as authority after loss of capacity. It must not
call all UK instruments an LPA.

## Security and privacy requirements

### Threats and safeguards

| Threat | Required safeguard |
| --- | --- |
| Account takeover | Prohibit credentials; mask identifiers; purpose-based access and export controls |
| Payment or mandate fraud | Separate verified provider contact from message-supplied details; preserve evidence and confirmation |
| Identity theft | Minimise names, addresses, dates, identifiers and statement retention |
| Phishing and impersonation | Encourage independent channel verification; show source and verification date |
| Financial abuse or coercion | Do not expose all accounts by default; support stop/escalate and private safeguarding notes |
| Unauthorised representative | Record authority evidence and restrictions; never infer authority from relationship |
| Device or file theft | Platform-private storage, encryption support, lock/access controls, safe previews and backups |
| Accidental sharing | Classification-aware reports, preview, masking, redaction and explicit destination |
| Stale guidance | Effective/verified dates, jurisdiction and links to current official sources |
| Over-collection | Field purpose and priority; safe references; retention reviews |
| Insider/support disclosure | Privacy-safe logs and diagnostics with no account values or statement contents |

### Always, optionally and never stored

**Always store when a relationship is recorded:**

- a non-sensitive account label, category, purpose, institution link, ownership
  type, status, relevant people, classification and last-reviewed date;
- enough masked identification to distinguish it from other relationships at
  the same institution;
- essential incoming/outgoing dependencies or an explicit `notReviewed` state;
  and
- provenance for operational instructions and authority claims.

**Store when useful and with informed choice:**

- full account/routing identifiers, IBAN, customer number, balances, statements,
  addresses, device locations, contact names, authority copies and tax evidence;
- card expiry, equipment serial number, contribution or beneficial-interest
  evidence and support needs; and
- all other Confidential values for which the user records a purpose,
  classification, access expectation and review/retention basis.

A safe location reference or masked value should be offered before a full value
or copied document.

**Never store:**

- online, mobile or telephone banking passwords and passcodes;
- PINs, CVV/CVC values, full payment-card numbers, magnetic-stripe or chip data;
- one-time passwords, transaction-signing codes, QR activation material,
  authenticator seeds, recovery codes or security answers;
- password-manager master credentials, device unlock codes or biometric data;
- live session cookies, access/refresh tokens or Open Banking authorisation
  credentials; and
- instructions for bypassing provider identity, authority, fraud or capacity
  controls.

These prohibitions apply to structured fields, notes, attachments, imports,
OCR, logs and support exports. Secret-shaped imported content must be rejected
or redacted before canonical storage.

## Reports and projections

Reports are purpose-limited projections of shared knowledge, not separate data
stores. Every report must state Clann, scope, generated date, classification,
staleness, exclusions and safe-handling guidance. Identifiers must be masked by
default; including Confidential detail requires explicit selection.

### Banking summary

Must show institutions, account labels/types/status, ownership, purpose,
currencies, authority readiness, essential dependencies, last review and open
actions. It should group UK deposit accounts by known authorised-firm/licence
group while warning that eligibility and limits require current verification.

### Direct Debit register

Must show mandate purpose, provider, masked reference, funding account,
frequency, variable/fixed status, essentiality, linked obligation, last seen
date and event-specific review action.

### Standing order and scheduled transfer register

Must distinguish external payees from transfers between household accounts and
show fixed amount, schedule, destination reference, purpose, essentiality and
review action.

### Regular income report

Must show payer, recipient, receiving account, frequency, dated amount, linked
needs and notification/redirection action. It must highlight income into an
account that may be restricted.

### Card and payment-permission register

Must show masked card/instrument identity, holder, status, linked account,
recurring-payment dependencies and separately visible Variable Recurring
Payment permissions and their limits. It must contain no prohibited card or
authentication data.

### Banking continuity checklist

Must generate event- and jurisdiction-specific actions with authority status,
essential-payment/income priorities, responsible person, status, evidence and
next step. It must not present generic actions as legal deadlines.

### Executor banking guide

Must combine the authorised institution inventory, document checklist, contact
log, date-of-death value work, payment/income dependencies, closure/transfer
status, unresolved questions and professional escalation flags.

### Attorney/deputy banking guide

Must combine authority restrictions, provider registration, separately issued
access, essential cash-flow needs, decision records, review duties and conflicts
without exposing donor credentials.

## Data model requirements

The banking module must extend the shared domain through entities and typed
relationships equivalent to:

- `FinancialInstitution`: legal entity, brand, jurisdiction, institution type,
  protection-group references and versioned contact routes;
- `BankingRelationship`: account category, purpose, status, servicing context,
  terms, currency and review information;
- `AccountIdentifier`: identifier type, masked display, protected value where
  permitted, issuer/country, classification and verification source;
- `AccountParty`: account, party, role, legal/beneficial interest, proportion,
  dates and evidence;
- `Authority`: representative, subject, authority type, jurisdiction, scope,
  restrictions, activation, status, evidence and institution registrations;
- `MoneyMovement`: incoming/outgoing direction, mechanism, payer/payee,
  account/instrument, schedule, dated amount, essentiality, obligation and
  event-specific actions;
- `PaymentPermission`: mandate/permission type, provider, limits, validity,
  cancellation/review route and evidence;
- `PaymentInstrument`: card/equipment type, masked identity, holder, account,
  status, location reference and replacement history;
- `AccountProductLink`: typed, dated relationship to a mortgage, liability,
  investment, pension, insurance, service, document or other account;
- `BalanceObservation`: amount, currency, effective time, source and purpose;
- `InstitutionInteraction`: actor, authority, channel, time, reference, request,
  outcome, documents shared and next action; and
- `ContinuityAction`: event, jurisdiction, priority, responsible role, status,
  source, evidence, due/review date and completion outcome.

Identifiers must be stable and opaque. Display labels, sort codes and account
numbers must not serve as database identity. Models must be schema-versioned,
support unknown/not-applicable distinctly, carry field-level classification and
provenance, and remain independent of PySide6 and any one report.

## Validation and business rules

1. An account requires category, purpose, institution, ownership type, status,
   classification and review state.
2. `unknown`, `notApplicable` and absent must have different meanings and must
   not be silently converted into one another.
3. Full identifiers must retain their protected value separately from masked
   display; logs, lists and default reports receive only masked values.
4. Format validation for sort codes, IBANs, BICs and identifiers checks syntax,
   not account existence, ownership or payment safety.
5. An ownership or authority relationship requires a source and cannot be
   inferred from a payment, statement addressee, cardholder or contact role.
6. An authority's scope, activation and restrictions must be evaluated before
   an action is described as authorised.
7. Money movement requires a payer/source, payee/destination, purpose, mechanism
   and at least a schedule or event trigger. Amount may be unknown or variable.
8. Cancelling a payment instruction must leave the linked obligation open until
   separately resolved.
9. Closing an account is blocked from `ready` status while unresolved essential
   payments, income, cards, linked products or retained-balance questions exist.
10. A balance without currency, effective time and source is invalid.
11. A legal entity/licence-group change must trigger deposit-protection review
    for linked accounts without rewriting historic observations.
12. Prohibited credential/card data must be rejected from structured fields and
    detected in free text/imports using explainable patterns plus user review.
13. Jurisdictional guidance requires source, effective/verified date and review
    date; expired guidance remains historical but cannot drive a current action.
14. Event recommendations must preserve user/institution overrides and their
    provenance rather than silently recomputing completed decisions.

## Non-functional requirements

### Privacy and security

- All core banking records, searches, reports and checklists must work locally
  and offline beneath the platform-resolved private `eolasDataRoot`.
- Encryption at rest, backup, export, redaction and secure-deletion controls
  must follow the Eolas privacy model and state their limits truthfully.
- Access and reports must be scoped to the active Clann and authorised role.
- Banking data must not be transmitted to analytics, support, AI or financial
  providers without a separate approved feature and explicit informed action.

### Accessibility

- Terms must use plain language with defined legal/payment terms and avoid
  assuming financial expertise.
- Reports must be keyboard/screen-reader accessible, printable, legible without
  colour and usable at 200 percent zoom.
- Event checklists must prioritise actions without alarmist language and expose
  detail progressively in any future UI.

### Auditability and reliability

- Creates, changes, merges, imports, authority updates, action decisions,
  report generation and deletion must be auditable with actor context, time,
  source and before/after values where policy permits.
- Historical ownership, authority, account status and institution interactions
  must be appendable without overwriting the factual past.
- A failed save or report must not leave partial canonical data or an
  apparently complete continuity action.

### Cross-platform and portability

- Domain behaviour must be independent of desktop platform and PySide6.
- Dates, currencies, addresses, routing identifiers, jurisdictions and names
  must not assume UK formats in the core model.
- Exported structured records must use open, versioned formats and preserve
  classifications, provenance and unknown values.

### Performance and scalability

- A Clann with 500 banking relationships, 10,000 money movements and 20 years
  of history must return an account summary or event checklist within 2 seconds
  on reference hardware, excluding opening evidence documents.
- Report generation must use bounded memory and must not expose records from a
  different Clann through caches or indexes.

### Testability

- Domain rules, reports and workflows must be testable without Qt, network
  access or real banking data.
- Tests must use conspicuously fictional institutions, identifiers and
  statements that cannot route payments or authenticate an account.
- Jurisdiction and time-dependent guidance must be injectable/versioned so
  tests do not depend on live websites or today's numeric limits.

## Acceptance criteria

### AC-1: Relationship inventory

1. Given fictional current, savings, joint, child, credit-card, fixed-term,
   foreign-currency, trust, business and online-only relationships, when they
   are recorded, then each has a category, purpose, institution, ownership,
   status, classification and review state without provider-specific fields in
   the shared core.
2. Given two trading brands sharing one authorised firm, when the banking
   summary is produced, then accounts remain linked to their familiar brands
   and are grouped under the same known protection entity with a dated
   eligibility warning.
3. Given an unknown mandatory fact, when the record is saved, then it is marked
   `unknown` with a follow-up rather than invented or omitted silently.

### AC-2: Ownership and authority

1. Given a joint account with unequal documented beneficial interests and an
   either-to-sign mandate, when reviewed, then legal holders, beneficial shares
   and signing rule remain separate facts with independent evidence.
2. Given an additional cardholder, next of kin and co-resident with no mandate,
   when authority is evaluated, then none is shown as an account owner or
   authorised representative.
3. Given an England-and-Wales property and financial affairs LPA with two joint
   attorneys and restrictions, when recorded, then jurisdiction, activation,
   joint action, restrictions, evidence and each institution's registration
   state are preserved.
4. Given Scottish or Northern Irish authority, when guidance is generated, then
   it uses the applicable instrument and source rather than relabelling it as an
   England-and-Wales LPA.

### AC-3: Identifiers, cards and secrets

1. Given permitted full account and routing identifiers, when ordinary lists,
   logs and reports are generated, then only masked values appear unless an
   authorised user explicitly selects a purpose-limited detailed report.
2. Given a full card PAN, PIN, CVV, password, one-time code, recovery code,
   authenticator seed or session token entered in a field, note or imported
   candidate, when validated, then canonical storage is blocked and the user is
   directed to a safe reference.
3. Given an IBAN that passes checksum validation, when displayed, then Eolas
   describes only format validity and does not claim the account exists or
   belongs to the recorded person.

### AC-4: Incoming and outgoing continuity

1. Given essential Direct Debits, a standing order, an internal transfer, a
   recurring card subscription and a Variable Recurring Payment, when recorded,
   then each retains its distinct mechanism, funding source, purpose, provider,
   schedule/limits, obligation link and event-specific action.
2. Given a payment instruction marked cancelled, when the linked contract is
   reviewed, then the contract remains unresolved until separately completed
   and the checklist warns that cancellation may not end the obligation.
3. Given salary, pension, benefit, dividend and rent entering sole and joint
   accounts, when a death or incapacity checklist is produced, then it identifies
   the recipient, receiving account, dependencies and provider-confirmation
   action without asserting that any income continues.
4. Given an account closure request with essential payments or incoming funds
   unresolved, when readiness is evaluated, then closure remains blocked and
   every dependency is listed.

### AC-5: Linked products and statements

1. Given a current account linked to mortgage payments, an offset mortgage,
   packaged insurance, a credit card and salary, when the account is changed,
   then the impact review lists every relationship without duplicating the
   linked product records.
2. Given a historical statement, when it is imported, then extracted accounts
   and payments remain candidates pending confirmation and the statement is not
   treated as proof of current status or balance.
3. Given original and redacted statement evidence, when provenance is followed,
   then both artifacts, their relationship, checksum, import attempt and source
   fields are identifiable subject to access controls.

### AC-6: Death workflow

1. Given sole, joint, credit, trust and business relationships after a fictional
   death, when the checklist is generated, then it prioritises authority,
   immediate needs, institution notification, essential dependencies,
   date-of-death evidence and estate reconciliation without asserting identical
   account treatment.
2. Given Tell Us Once is marked completed, when outstanding contacts are shown,
   then private banks, card issuers, private pensions and other uncovered
   providers remain until separately confirmed.
3. Given a joint survivor can operationally access an account, when estate work
   is reviewed, then beneficial ownership, contributions and tax/professional
   questions remain visible rather than treating access as conclusive ownership.
4. Given the actor knows the deceased person's PIN and login, when the guide is
   produced, then it prohibits their use and directs the actor to the provider's
   bereavement/authority route.

### AC-7: Incapacity and temporary events

1. Given a diagnosis without a decision-specific capacity determination or
   financial authority, when the incapacity workflow runs, then Eolas does not
   transfer control and flags authority verification.
2. Given a registered representative, when an institution has not registered
   that authority, then Eolas distinguishes legal evidence from provider access
   readiness and tracks the registration action.
3. Given a person with capacity needs six weeks of hospital assistance, when a
   temporary plan is recorded, then its authorised scope, essential actions,
   start/end dates and revocation review are captured without sharing
   credentials.
4. Given a lost phone and card overseas, when the emergency checklist is
   generated, then independently verified contacts, incident references,
   alternate essential funding and recurring-payment review are included, with
   no stored recovery secrets.

### AC-8: Reports and privacy

1. Given the same fictional Clann, when all seven required reports are
   generated, then each states scope/date/classification, uses shared canonical
   records, masks identifiers by default and identifies stale or unknown data.
2. Given a report containing Confidential fields, when export is requested,
   then the user sees the included categories and destination risk and must
   explicitly confirm; cancellation creates no export.
3. Given a representative without access to a protected account, when they
   query reports or search, then no value, count, contact or existence signal
   from that account or another Clann is disclosed.

### AC-9: Guidance currency and jurisdiction

1. Given a changed deposit-protection limit or provider process, when guidance
   is updated, then historic observations retain their old source/date while new
   checklists use the approved current version and no account record is silently
   rewritten.
2. Given guidance past its review date, when it would drive an action, then the
   action requires current verification and cannot be presented as confirmed.
3. Given a non-UK account, when recorded, then currency, routing, ownership,
   authority and protection fields accept the relevant jurisdiction without a
   UK sort code, LPA, probate or FSCS assumption.

### AC-10: Audit, accessibility and performance

1. Given record corrections, account closure, authority change, imported
   statement, completed checklist action and deletion, when history is queried,
   then actor context, time, source and permitted before/after facts explain
   each outcome without exposing prohibited secrets in logs.
2. Given keyboard-only use, a supported screen reader, high contrast and 200
   percent zoom, when every required report and workflow is exercised, then all
   information, states and actions remain perceivable and operable without
   colour alone.
3. Given the reference dataset of 500 accounts, 10,000 money movements and 20
   years of history, when reports are generated in three consecutive runs, then
   each meets the 2-second target and contains records only from the active
   Clann.
4. Given network access is denied, when all banking records, workflows and
   reports are used, then they complete without a remote call; dated guidance
   remains available with its last verified status.

## Future opportunities

Each item requires a separate approved requirement, privacy assessment and,
where it changes trust boundaries, an ADR:

- read-only Open Banking account discovery and refresh with explicit consent,
  regulated-provider checks, token custody, revocation and offline fallback;
- statement analysis and assisted reconciliation through the Document Import
  Framework;
- subscription, recurring-payment and regular-income detection with explainable
  confidence and confirmation;
- dormant or forgotten account detection and guided tracing;
- duplicate institution/account resolution and closed-account suggestions;
- reminders for maturity, review, card expiry, authority renewal and stale
  contacts;
- continuity-readiness insights based on missing dependencies and unresolved
  actions, without scoring a family for refusing optional sensitive fields;
- protection-group exposure review using dated official reference data;
- anomaly and fraud-warning assistance without claiming fraud detection;
- cash-flow projections and essential-payment resilience scenarios; and
- controlled collaboration with executors, attorneys and advisers using
  purpose-limited access and audit.

## Out of scope

The initial Banking module does not include:

- bank login, balance refresh, payment initiation or account servicing;
- Open Banking connections, credential/token custody or automated bank feeds;
- storing or testing any prohibited credential, card-security or recovery data;
- a double-entry ledger, bookkeeping system, budgeting engine, tax calculation
  or personal financial-management service;
- transaction categorisation, subscription detection, fraud detection,
  continuity scoring or automated recommendations;
- automatic cancellation, redirection, closure, transfer or notification;
- automatic ownership, capacity, authority, survivorship, tax or probate
  conclusions;
- personalised legal, tax, investment, credit, debt or financial advice;
- guarantee of deposit-protection eligibility, account authenticity, balance,
  institution response or secure physical deletion;
- a provider directory whose contact details are assumed current without
  verification;
- document-import implementation beyond the separate requirement 008; or
- UI layout, widgets, navigation or visual design.

## Dependencies and decisions

### Requirements

- Requires [002](002-privacyAndSecurityModel.md) for classification,
  minimisation, private storage, sharing, retention and disposal.
- Requires the shared concepts in [003](003-handbookContentStructure.md) and the
  domain guidance referenced below.
- Related to [007](007-legalDocumentCustodyAndAccess.md) for authoritative legal
  document custody and access.
- Integrates with [008](008-documentImportFramework.md) for statement evidence
  and reviewed extraction proposals.

### Architecture Decision Records

- [ADR-0002](../../adr/002-offlineFirst.md): all core banking knowledge remains
  usable offline.
- [ADR-0003](../../adr/003-neverStorePasswords.md): credentials are prohibited.
- [ADR-0004](../../adr/004-publicTemplatesPrivateData.md): real banking data
  remains outside the public project.
- [ADR-0005](../../adr/005-informationClassification.md): field-level handling
  and fail-closed defaults.
- [ADR-0006](../../adr/006-sharedDomainModel.md): banking concepts are shared
  across projections.
- [ADR-0007](../../adr/007-knowledgeBeforeDocuments.md): statements and reports
  do not define canonical knowledge.
- [ADR-0008](../../adr/008-handbookAsProjection.md): reports are projections.
- [ADR-0011](../../adr/011-platformPrivateDataRoot.md): platform-private local
  storage.

### Decisions still required

- Approved banking entity and relationship extensions to the shared domain
  model.
- Default classification and masking for each identifier and report.
- Jurisdiction-content packaging, ownership and update/review process.
- Retention rules for balance observations, statements, institution contacts and
  representative action logs.
- Role-based access and report-sharing policy for executors, attorneys, advisers
  and other trusted people.

## Authoritative research references

These sources inform the requirement but are not copied into canonical records.
They must be checked for currency before guidance is released:

- [GOV.UK: Manage a bank account for someone else](https://www.gov.uk/government/publications/deputy-and-attorney-guidance-dealing-with-banks)
  (England and Wales; authority evidence and joint-account considerations).
- [GOV.UK: Property and financial affairs attorney duties](https://www.gov.uk/manage-lasting-power-attorney/property-financial-affairs)
  (separation, proof and attorney responsibilities).
- [GOV.UK: Tell Us Once](https://www.gov.uk/after-a-death/organisations-you-need-to-contact-and-tell-us-once)
  (scope of government notifications and separately contacted organisations).
- [FCA: Bereavement and power-of-attorney review](https://www.fca.org.uk/news/press-releases/fca-probes-banks-bereavement-power-attorney-policies)
  (consumer vulnerability and the need for adaptable institution support).
- [MoneyHelper: Joint accounts](https://www.moneyhelper.org.uk/en/everyday-money/banking/joint-accounts)
  (operation, incapacity and death considerations).
- [MoneyHelper: Direct Debits, standing orders and recurring card
  payments](https://www.moneyhelper.org.uk/en/everyday-money/banking/direct-debits-and-standing-orders.html)
  (mechanism and contract-cancellation distinctions).
- [MoneyHelper: Paying funeral costs from an account](https://www.moneyhelper.org.uk/en/family-and-care/death-and-bereavement/help-paying-for-a-funeral)
  (provider-dependent direct payment and prohibition on credential use).
- [FSCS: Deposit protection limit](https://protected.fscs.org.uk/what-we-cover/banks-building-societies-credit-unions/deposit-limit-increase/)
  and [temporary high balances](https://protected.fscs.org.uk/making-a-claim/claims-process/temporary-high-balances/)
  (current UK limits, aggregation and time-limited additional protection).
- [Open Banking: Variable Recurring Payments](https://www.openbanking.org.uk/variable-recurring-payments-vrps/)
  (permission parameters and evolving availability).
- [GOV.UK: Dormant Assets Scheme](https://www.gov.uk/government/publications/the-dormant-accounts-scheme)
  (account tracing and continuing reclaim rights).

## Verification

- Review the model against at least one conspicuously fictional scenario for
  each relationship category and actor role.
- Run death, incapacity, hospital, overseas and moving-home walkthroughs with
  executor, attorney, survivor and adviser perspectives.
- Trace all captured fields to a continuity purpose, priority, classification
  and report/workflow use; remove fields without a justified use.
- Complete jurisdiction review for England and Wales, Scotland and Northern
  Ireland before publishing jurisdiction-specific guidance.
- Complete legal/financial subject-matter review of guidance while preserving
  the product's non-advice boundary.
- Test all reports for masking, classification-aware export, stale guidance,
  accessibility, offline operation and cross-Clann isolation.
- Scan code, fixtures, documentation and generated reports for prohibited
  credential fields, usable account/card identifiers and real private data.

## Traceability

- Implementation: pending
- Tests: pending
- Documentation: [product vision](../../../documentation/productVision.md),
  [principles](../../../documentation/principles.md),
  [domain model](../../../documentation/domainModel.md),
  [glossary](../../../documentation/glossary.md),
  [information classification](../../../documentation/informationClassification.md),
  [privacy and security](../../../documentation/privacyAndSecurity.md),
  [Money and Pensions handbook chapter](../../../handbook/05-MoneyAndPensions.md)
- Principles: [P-001, P-002, P-003, P-004, P-005, P-007, P-008, P-009 and
  P-010](../../../documentation/principles.md)
- Pull request: pending
- Agent runs: 2026-07-31 - Codex, initial Banking module domain requirements
  specification based on the maintainer brief and authoritative UK sources.

## Change history

- 2026-07-31: created as the Banking module domain and continuity requirement.
