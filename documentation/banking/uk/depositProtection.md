# UK banking deposit protection

## Guidance metadata

| Field | Value |
| --- | --- |
| Jurisdiction | United Kingdom |
| Status | Current guidance; verify before relying |
| Verified | 2026-07-31 |
| Next review | 2026-10-31, or earlier after a PRA/FSCS rule change |
| Owner | Project maintainers |
| Requirement | [009: Banking module](../../../project/requirements/features/009-bankingModule.md) |

## Current position

As verified on 2026-07-31, the Financial Services Compensation Scheme (FSCS)
states that eligible deposits with a failed UK-authorised bank, building society
or credit union are normally protected up to **GBP 120,000 per eligible person,
per authorised firm**. The limit applies across accounts and trading brands that
share the same banking licence, not separately to every account or brand.

The limit increased from GBP 85,000 on 2025-12-01. Historic observations must
use the rule applicable on their relevant date.

Certain qualifying temporary high balances may be protected up to **GBP 1.4
million for six months**. Eligibility, start date, joint-account treatment and
exceptions depend on the event and current rules; personal-injury balances may
receive different treatment.

## Eolas guidance

- Record the legal authorised firm and shared licence group separately from the
  familiar trading brand.
- Treat protection as `confirmed`, `likely`, `notCovered` or `unknown`, with
  source and verification date. Eolas must not guarantee eligibility.
- Aggregate relevant accounts by eligible person and authorised firm only for a
  dated review; do not store the current limit as an account attribute.
- Flag a property sale, inheritance, insurance payment or other possible
  temporary-high-balance event for current-rule review.
- Re-check protection after a provider merger, licence change, balance event or
  guidance review date.
- Use the FSCS protection checker or official guidance before relying on a
  calculated exposure.

## Official sources

- [FSCS deposit limit increase](https://protected.fscs.org.uk/what-we-cover/banks-building-societies-credit-unions/deposit-limit-increase/)
- [FSCS temporary high balances](https://protected.fscs.org.uk/making-a-claim/claims-process/temporary-high-balances/)
- [FSCS deposit protection questions](https://protected.fscs.org.uk/industry-resources/deposit-protection-banks/)

## Change history

- 2026-07-31: created from guidance previously embedded in requirement 009.
