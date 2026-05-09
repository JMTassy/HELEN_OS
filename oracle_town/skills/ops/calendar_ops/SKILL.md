---
id: calendar_ops
label: Calendar
icon: 📅
domain: ops
status: ready
ledger_enabled: true
---

Load this skill when the user asks to manage planning, schedule meetings, track deadlines, set follow-ups, or review upcoming events and commitments.

## Actions
- log_appointment — record a meeting or call
- set_deadline — add a project deadline with owner
- plan_week — produce a structured weekly plan
- flag_followup — flag a date for a follow-up action
- review_calendar — summarize upcoming commitments

## Reads
- oracle_town/skills/ops/calendar_ops/references/

## Writes
- artifacts/calendar/<week-id>/

## Gotchas
- All deadline memory must write a receipt to be sovereign-admissible
- Dates must always be stored as absolute ISO 8601 (never "next Thursday")
