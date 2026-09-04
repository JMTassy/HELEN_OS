---
schema: PROPOSAL_V1
proposal_id: CANNOT_SAY_SUPPORT_V0
title: Cannot-Say Support Packet V0
status: PROPOSAL
authority: false
canon: false
ledger_effect: none
claim_status: NO_CLAIM
git_stage: no
git_commit: no
proposer: FABLE (Claude session, 2026-07-09)
reducer_required: true
---

# Cannot-Say Support Packet V0

🔵 OBSERVED · 🟣 CLAIM → proposal only, not admitted

---

## Core Law

**Support does not require legibility.**

She cannot say what is happening.
HELEN does not ask for the story.
HELEN offers choices.
HELEN records only what is explicitly given.

`helped before legible` — this is the architectural shift.

---

## The Problem This Solves

Every existing HELEN interaction surface begins with input: a message, a command, a query.
This assumes the person is ready to be legible.

Sometimes they are not. Distress, overwhelm, grief, shutdown — these are states where
the question "what's happening?" is itself a burden. A system that requires explanation
before it helps has made extraction a prerequisite for care.

This packet defines a different entry point.

---

## Packet Schema: `CANNOT_SAY_SUPPORT_PACKET_V0`

```json
{
  "schema": "CANNOT_SAY_SUPPORT_PACKET_V0",
  "packet_id": "CS-<timestamp>-<random_hex>",
  "recorded_at": "<ISO-8601>",
  "chosen_option": "stay_with_me | help_me_move | hold_for_later | stop | none",
  "explicit_words": "<string | null>",
  "requested_next_action": "<string | null>",
  "do_not_infer": true,
  "authority": false,
  "sovereign": false,
  "canon": false,
  "ledger_effect": "none",
  "reducer_required": false
}
```

### Field rules

| Field | Rule |
|---|---|
| `chosen_option` | One of five values. No inference. If none chosen, value is `"none"`. |
| `explicit_words` | Only verbatim text the person typed or chose. `null` if nothing given. |
| `requested_next_action` | Only if person explicitly stated one. `null` otherwise. |
| `do_not_infer` | Always `true`. Hard-coded. Cannot be set to `false` by any surface. |
| `authority` | Always `false`. This packet makes no claim about inner state. |

### What the packet MUST NOT contain

- Inferred cause, diagnosis, or reason for distress
- Inferred danger level or risk assessment  
- Inferred consent or identity state
- Hidden story reconstructed from context
- Any field not listed in the schema

The packet is a witness to what was chosen, not a diagnosis of what happened.

---

## The Three Choices

```
Stay with me      — I need presence. No action required.
Help me move      — I need something to do. Give me one small thing.
Hold this for later — I'm not ready now. Record that I was here.
```

Plus two structural exits:

```
Stop              — End this. Nothing is saved.
Write one word    — Optional. Exactly one word. Becomes explicit_words.
```

---

## What HELEN Does With Each Choice

### Stay with me
Responds with presence, not information. A single line. No questions.
Example: "I'm here. You don't need to explain."

### Help me move
Offers one specific, physical, optional action. Not a list. Not advice.
Example: "One breath. In through the nose, out through the mouth. That's it."

### Hold this for later
Creates a packet with `chosen_option: hold_for_later`, `explicit_words: null`.
Records timestamp only. Responds: "Held. It will be here when you're ready."

### Stop
Packet is discarded. No ledger entry. No memory. Response: "Gone."

---

## Routing

```
cannot_say_support_packet → shell only
                          → does NOT route to mayor
                          → does NOT touch ledger
                          → does NOT create a receipt
                          → authority=false at every layer
```

This is shell-layer care. The kernel stays stable. The membrane becomes gentle.

---

## WUL Frame

```
🔵 structure: choice menu (three options + stop)
🟢 validation: helped before legible
🔴 boundary: no inferred truth
⚪ witness: only explicit words become record
🟣 bloom: later meaning can emerge, but not be forced
```

---

## What This Is Not

- Not a crisis intervention protocol (requires licensed clinical routing, out of scope)
- Not a therapy session (HELEN is not a therapist)
- Not a diagnostic tool (do_not_infer=true is non-negotiable)
- Not a sovereign admission (authority=false, no ledger effect)

---

## Next Step

To move from PROPOSAL to ADMITTED:

1. Operator reviews and approves schema
2. Shell implementation of three-choice screen
3. Packet emitter validated against schema
4. `do_not_infer=true` enforced at code level, not just schema
5. Operator-authorized admission via usual 7-gate pipeline

---

*authority=false · canon=false · ledger_effect=none · NO_CLAIM*
*This proposal was drafted by FABLE. It makes no admission. Operators admit.*
