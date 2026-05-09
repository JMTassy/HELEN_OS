---
id: client_crm
label: Clients
icon: 👥
domain: crm
status: ready
ledger_enabled: true
---

Load this skill when the user asks to manage clients, contacts, follow-ups, opportunities, or relationships. JMT Consulting CRM layer.

## Actions
- add_contact — create a new client record
- log_interaction — record a meeting, call, or email
- set_followup — schedule a follow-up action
- build_opportunity — describe a new commercial opportunity
- generate_brief — produce a client brief or account summary

## Reads
- oracle_town/skills/ops/client_crm/references/client_schema.md
- oracle_town/skills/ops/client_crm/references/followup_templates.md

## Writes
- artifacts/crm/<client-id>/

## Gotchas
- Never push client names or PII to remote without explicit operator approval
- Follow-ups must write a receipt to confirm they were scheduled, not just noted
