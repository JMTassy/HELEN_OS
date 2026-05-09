# Skill Pastilles — Visual Operating Language

## Doctrine

**pastille = visible Skill node**
**Skill = actionable capability**
**receipt = action proof**
**ledger = memory of Skill activity**

A pastille is not an icon, tag, or decoration. It is a live entry point into a runnable Skill module. Every pastille represents a bounded capability with defined actions, a status, and a ledger connection.

## Vocabulary

| Term | Definition |
|---|---|
| pastille | Visual capsule on the constellation canvas representing one Skill |
| Skill | A bounded, named capability with actions, reads/writes, and a SKILL.md |
| action | A named operation within a Skill (e.g. `write_script`, `create_invoice`) |
| receipt | Proof that a Skill ran — hash-chained, written to the ledger |
| status | `ready` = available, `active` = running, `blocked` = waiting for dependency |

## Visual Rules

- HELEN portrait at center — sovereign anchor, never moved
- 8 Skill pastilles on inner orbit (radius ~195px from center), equally spaced
- Pastille shape: rounded capsule, icon (left) + label (right) + status dot
- Signal amber border when selected; dim border at rest
- Dashed connector line from pastille to center (breaks at HELEN's exclusion zone)
- Background semantic dots: outer field only, smaller, force-simulated
- AIRI status indicator: green dot = live bridge, silver = offline

## Orbit Geometry

- Inner orbit radius: 195px (skill pastilles)
- Avatar exclusion zone: 80px from center
- Background semantic field: beyond 245px from center (soft gravity ring)

## Detail Panel

When a Skill pastille is clicked:
1. Detail panel opens at bottom of center column
2. Shows: icon + label + domain badge + description
3. Lists: all available actions as capsule tags
4. Provides: "Run Skill" (placeholder) and "Write Receipt" (placeholder) buttons
5. Shows HELEN witness phrase: "I witness this {domain} skill."
6. Fires `/api/witness` → pushes spark:notify to AIRI if connected

## Skill MVP (8 modules)

| ID | Label | Domain |
|---|---|---|
| video_studio | Video Studio | media |
| jmt_admin | JMT Admin | admin |
| client_crm | Clients | crm |
| offer_builder | Offers | sales |
| content_engine | Content | content |
| research_brief | Research | intelligence |
| calendar_ops | Calendar | ops |
| sovereign_ledger | Ledger | governance |

## Constraints

- Skill pastilles are NON_SOVEREIGN — they are entry points, not kernel actors
- "Run Skill" and "Write Receipt" are placeholders until wired to actual workflow
- The ledger (sovereign_ledger skill) is the only read-only Skill — it may never write to town/ledger_v1.ndjson directly
- HELEN avatar placement is fixed; never used as an action button; never replaced by AURA
