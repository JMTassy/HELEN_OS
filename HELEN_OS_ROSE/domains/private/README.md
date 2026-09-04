# Domain: Private — rules only, no content

Privacy classes governed here: `PERSONAL_PRIVATE`, `MEDICAL_PRIVATE`,
`LEGAL_PRIVATE`, `FINANCIAL_PRIVATE`.

This folder intentionally stores **rules about** sensitive information,
never the information itself. No personal history, health detail, family
or relationship matter, residency question, legal case, or account number
belongs anywhere in this repository.

Rules:

1. Business strategy files must not reference private matters. If a
   strategic decision genuinely depends on one (e.g., time availability,
   location constraints), the strategy file records only the constraint's
   effect ("limited on-site weeks in Q4"), never its cause.
2. A synthesis that would span this partition and any business partition
   requires an explicit Rose decision in the ledger, and its output stays
   in the most restrictive class involved.
3. Operators load nothing from private context by default. Minimum
   necessary context is the standing order (`OPERATING_CONTRACT.md` §6).
4. If sensitive material is found committed anywhere in this repository,
   removing it is an immediate `NOW` priority and a note goes to the
   weekly review.
