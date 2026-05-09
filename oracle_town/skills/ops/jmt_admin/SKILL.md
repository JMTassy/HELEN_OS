---
id: jmt_admin
label: JMT Admin
icon: 🧾
domain: admin
status: ready
ledger_enabled: true
---

Load this skill when the user asks about JMT Consulting administration: invoices, quotes, documents, société, legal, accounting, or anything related to running the consulting firm.

## Actions
- create_invoice — generate invoice from client + amount + services
- create_quote — generate devis from brief or offer
- draft_contract — produce consulting agreement from template
- admin_report — summarize administrative state of the firm
- document_archive — locate or file a company document

## Reads
- oracle_town/skills/ops/jmt_admin/references/company_profile.md
- oracle_town/skills/ops/jmt_admin/references/invoice_rules.md

## Writes
- artifacts/admin/<document-type>-<date>/

## Gotchas
- JMT Consulting entities must NEVER be named in pushed/public artifacts
- TAR Paris + Corsica Studio + Calvi on the Rocks + Corsican RE are the portfolio entities
- Always use NON_SOVEREIGN for generated documents; only MAYOR can sign sovereign records
