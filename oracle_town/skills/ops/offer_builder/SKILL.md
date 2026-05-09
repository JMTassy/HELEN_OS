---
id: offer_builder
label: Offers
icon: 📦
domain: sales
status: ready
ledger_enabled: true
---

Load this skill when the user wants to create a commercial offer, consulting proposal, pack, pitch deck, or PDF proposal for a client or investor.

## Actions
- build_consulting_pack — structure a consulting service package
- draft_proposal — produce a full commercial proposal doc
- create_pitch — generate pitch deck outline or narrative
- price_offer — suggest pricing for a scope of work
- export_pdf_brief — format for PDF export

## Reads
- oracle_town/skills/ops/offer_builder/references/consulting_packages.md
- oracle_town/skills/ops/offer_builder/references/proposal_template.md
- docs/style/uzik-writing-style.md

## Writes
- artifacts/offers/<offer-id>/

## Gotchas
- UZIK writing style applies to all external copy: deck tone, not chatbot tone
- Negative parallelism is hard-banned in client-facing copy
- Never include AI attribution in client documents
