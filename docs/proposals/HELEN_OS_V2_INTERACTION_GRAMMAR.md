# HELEN OS v2 — Interaction Grammar Lock (Proposal)

NO CLAIM — NO SHIP — PROPOSAL ONLY — CANDIDATE_GRAMMAR_LOCK

```
artifact_type:         PROPOSAL_GRAMMAR_LOCK
proposal_id:           HELEN_OS_V2_INTERACTION_GRAMMAR
authority:             NON_SOVEREIGN
canon:                 NO_SHIP
lifecycle:             PROPOSAL
implementation_status: NOT_IMPLEMENTED
memory_class:          CANDIDATE_GRAMMAR
captured_on:           2026-04-27
parent_proposal:       docs/proposals/HELEN_OS_V2_USER_CENTRIC_UX.md
sibling_proposals:     docs/proposals/FOCUS_MODE_TERMINAL_SPEC.md
                       docs/proposals/HELEN_OS_V2_VISUAL_CANON_LOCK.md
                       docs/proposals/TEMPLE_MODE_VISUAL_BRIEF.md
related_memory:        project_helen_os_v2_product_model.md
                       feedback_helen_protagonist_not_hologram.md
                       feedback_ralph_violations.md
```

> **Core thesis**
> HELEN is not a screen. HELEN is a behavior over time.

> **Product loop**
> intent → suggestion → confirmation → receipt → calm

> **Interaction grammar**
> click → propose
> confirm → mutate
> mutate → receipt
> receipt → ledger
> ledger → memory

---

## §1. Executive Summary

- **The product is the loop, not the dashboard.** HELEN OS is a behavior
  over time, not a screen full of intelligence. Future UI, clips,
  terminal flows, and prototypes must align to the same behavioral
  contract.
- **HELEN OS must feel obvious, calm, and inevitable.** The win
  condition is the operator thinking *"why doesn't this exist already?"*
  — not *"this is impressive."*
- **The interface must hide complexity until it is needed.** Hide more,
  not add more. Idle is sparse. Density is opt-in.
- **HELEN suggests. The user decides. Everything is recorded.** This is
  the product tagline, locked. Every arrow in the grammar serves it.

This proposal locks the experience loop and the five-arrow grammar so
that every downstream surface (Focus Mode CLI, GUI, video clip, Witness
Mode dashboard, Oracle / Temple modules) inherits the same contract.

---

## §2. Canonical Experience Loop

The default Focus Mode demonstration is an 8-scene loop. Any
demonstration medium (terminal session, cinematic clip, GUI prototype)
must respect this scene order.

| # | Scene | Arrow served |
|---|---|---|
| 1 | Calm idle | (no arrow yet) |
| 2 | User intent appears | (operator input) |
| 3 | HELEN proposes | click → propose |
| 4 | User selects one proposal | (operator selection — pre-confirm) |
| 5 | Receipt confirmation | confirm → mutate (pre-write) |
| 6 | Execution | mutate → receipt |
| 7 | Ledger updates | receipt → ledger |
| 8 | Return to calm | ledger → memory |

**Canonical example intent (locked):**

> *"Prepare my Q3 product strategy from notes, market research, and recent emails."*

This intent is the reference example for every demonstration. It is
practical, work-shaped, and emphatically not mystical — guarding
against the "meditation app" failure mode.

---

## §3. Scene Details

### Scene 1 — Calm idle

- HELEN core breathing
- `No new mutations`
- subtle waveform
- LEGORACLE pill: `Gate Clear · No Active Claim`

The default surface. Nothing demanding the operator's attention.
99% of sessions, 100% of the time.

### Scene 2 — User intent appears

- the operator types or speaks the intent
- intent line populates: *"Prepare my Q3 product strategy from notes,
  market research, and recent emails."*
- no proposals yet
- the surface stays still otherwise

### Scene 3 — HELEN proposes

- three action cards slide in
- soft glow only — no dashboard expansion
- each card carries an explicit `[PROPOSAL]` label
- example proposals: `Research competitors` / `Synthesize key patterns`
  / `Draft Q3 strategy`
- nothing else changes on screen

### Scene 4 — User selects one proposal

- user selects one (single key in terminal, click in GUI)
- gentle highlight on the selected card
- **no mutation yet** — selection is not confirmation
- the other two cards dim slightly but remain visible

### Scene 5 — Receipt confirmation

A small sheet:

```
Proposed action:  Draft Q3 strategy
Policy:           PASS
Mutation:         Document creation
                  [ Cancel ]   [ Confirm ]
```

This is the **only** path through which a Focus Mode action enters
the spine. Cancel returns to Scene 1 with no event written.

### Scene 6 — Execution

- execution pulse — tiny, on the receipt pill
- no banner, no spinner, no "AI thinking…", no celebration
- the pulse lasts long enough to register, no longer

### Scene 7 — Ledger updates

```
Latest receipt: STRATEGY_DRAFTED · APPENDED
```

The receipt class is determined by the actual mutation type. The pill
flashes ~3 seconds with the new hash, then settles.

### Scene 8 — Return to calm

- same quiet surface as Scene 1
- the only difference: ledger pill now shows the new last receipt
- LEGORACLE pill returns to `Gate Clear · No Active Claim`

The loop has completed. The system is calm again. The next intent can
arrive.

---

## §4. Interaction Grammar Contracts

For each arrow, the contract specifies five fields:
who initiates, who authorizes, what is visible, what is recorded,
what is forbidden.

### Arrow 1 — `click → propose`

| Field | Contract |
|---|---|
| Who initiates | OPERATOR (click / keypress / voice / declared intent) |
| Who authorizes | (none — no authorization needed for a proposal) |
| What is visible | proposal text + `[PROPOSAL]` label, max 3 proposals per intent |
| What is recorded | `EFFECT_PROPOSED` event, AI-authored (HELEN's proposal) or OPERATOR-authored (operator declaring intent / source) |
| Forbidden | acting on the trigger; mutating; writing anything other than `EFFECT_PROPOSED`; emitting more than 3 proposals; sacred / 8D / mystical phrasings (caught by language firewall) |

### Arrow 2 — `confirm → mutate`

| Field | Contract |
|---|---|
| Who initiates | OPERATOR only |
| Who authorizes | OPERATOR alone — AI cannot self-confirm |
| What is visible | confirmation sheet (Scene 5) — proposed action, policy, mutation, Cancel / Confirm |
| What is recorded | `OPERATOR_DECISION` event, OPERATOR-authored (replay-time invariant) |
| Forbidden | autoconfirmation; time-based confirmation; batch confirmation across multiple proposals; AI-as-operator forgery (rejected at fold-time) |

### Arrow 3 — `mutate → receipt`

| Field | Contract |
|---|---|
| Who initiates | the policy gate, after operator confirmation |
| Who authorizes | SYSTEM (gate authorization event) and RUNTIME (sandbox execution event) |
| What is visible | brief status line in Focus; full receipt JSON in Witness |
| What is recorded | `EFFECT_AUTHORIZED` (SYSTEM) → `EFFECT_EXECUTED` or `EFFECT_FAILED` (RUNTIME); or `EFFECT_DENIED` (SYSTEM) if the gate refuses |
| Forbidden | mutation without an immediately-following receipt; receipt-first/mutate-later; mutation-only/receipt-later |

### Arrow 4 — `receipt → ledger`

| Field | Contract |
|---|---|
| Who initiates | RUNTIME (the canonical writer) |
| Who authorizes | hash-chain integrity is the authorization; no other actor |
| What is visible | ledger pill in Focus; full NDJSON tail in Witness |
| What is recorded | append-only NDJSON entry, hash-chained to `prev_event_hash` |
| Forbidden | direct ledger writes outside the canonical writer (`tools/helen_say.py` for the sovereign spine; scope-internal ledger primitives for `experiments/helen_mvp_kernel/`); in-place edits; non-canonical canonicalization |

### Arrow 5 — `ledger → memory`

| Field | Contract |
|---|---|
| Who initiates | the reducer, on every fold |
| Who authorizes | (none — the reducer is pure) |
| What is visible | quiet — counters change without announcement in Focus; reducer state diff in Witness |
| What is recorded | derived state only: counters, last verdict, last event hash, terminated flag |
| Forbidden | hidden state outside reducer output; memory writes that bypass the ledger; memory that contradicts ledger replay |

---

## §5. Hide More Rule

**hide more, not add more.**

Operator correction 2026-04-27. The interface was drifting back
toward "rich UI system" — too persistent left sidebar, too many
visible modules, feeling closer to a productivity app than to an
intelligence layer of an OS.

The corrected rule:

- **No persistent left sidebar by default.** A sidebar is a Witness Mode
  surface, not a Focus Mode default.
- **No permanent module wall.** The dock is not a macOS dock — it is
  not always-rendered.
- **No always-on rich dashboard.** Dashboard belongs in Witness Mode.
- **Channels collapse to glyphs by default.** The right-side channels
  panel reduces to a single dot at idle; expands only when a channel is
  actively producing input or has unread state.
- **Dock / modules collapse to a quiet rail by default.** A single
  `:` glyph or a one-line minimum-height rail; the operator opens the
  full dock via colon-prefix command, never seeing the full module
  list by default.
- **Advanced structure belongs in Witness Mode.** If a surface is "for
  inspecting the system," it does not appear in Focus.

This rule supersedes the ASCII-layout illustration in
`HELEN_OS_V2_USER_CENTRIC_UX.md` §4 to the extent of any conflict.
The textual contract (5 elements + small contextual channels panel +
mode toggle) remains; the visual density should reduce in any rendered
mockup.

---

## §6. Focus Mode Amendment

The Focus Mode idle surface — after applying §5 — should show only:

1. **HELEN Intelligence Core** (the calm presence — embodied per
   `feedback_helen_protagonist_not_hologram.md`)
2. **Current intent** (one line in the operator's language)
3. **Up to 3 proposals**, only when relevant (post-intent, pre-confirm)
4. **Compact ledger pill** (single line)
5. **Subtle voice input/output** (two small waveforms — opt-in via
   `:settings voice meter on` per `FOCUS_MODE_TERMINAL_SPEC §6.5`)
6. **Minimal mode switch** (`[ FOCUS ]` active label only; the
   `| witness` text is shown but minimal)
7. **Quiet module rail** (one glyph or a single muted line; full dock
   opens only on `:` command)

Nothing else. No persistent overlays, no telemetry, no LEGORACLE
verdict banners, no claim status, no capacity meters, no OS noise.

This amendment supersedes any conflicting elements in the parent
UX proposal §4 layout.

---

## §7. Witness Mode Boundary

Witness Mode is the **only** place where system inspection belongs:

- full ledger (raw NDJSON tail, paginated, filterable)
- policy gates (K8 / K-tau / K-rho / K-wul status, last verdicts)
- claim workflow (active claims, evaluator pipeline, verdicts)
- reducer state (skill promotion reducer, bridge classifier outputs)
- LEGORACLE verdicts (`SHIP_AUTHORIZED` / `SHIP_FORBIDDEN` / `DENIED`
  / `PENDING_RECEIPT`) — surfaced **only during active claim evaluation**
- firewalls (language + desire — classifier state, recent blocks)
- diagnostics (capacity meters, OS noise, worker lanes)
- constitution strip (kernel boot manifest, mayor key registry, schema
  registry status, ghost closure detector, knowledge compiler)

**Hard boundary**: Witness complexity must not leak into Focus Mode.
If a surface is in the list above, it does not appear in Focus Mode by
default. A drill-down link from a Focus pill (e.g. tapping the ledger
pill) may flip the operator to a Witness sub-surface, but the flip is
explicit, never automatic, and reversible at all times.

---

## §8. Product Feeling

The target feeling, in priority order:

> *"This feels obvious. Why doesn't this exist already?"*

**Not** the target feeling:

> *"This is impressive."*

The first reaction means the product is so well-shaped that it reads
as inevitability — the operator stops noticing the cleverness because
the loop fits the work. The second reaction means the product is
showing off, which is a diagnostic of the "rich UI system" failure
mode §5 corrects.

Every design review, mockup, clip, and prototype should be tested
against this binary: *obvious* or *impressive*. Choose obvious.

---

## §9. Clip Usage

The 8-scene loop locked in §2 / §3 can later become:

- **Teaser** — public-facing short, social/embed-shaped
- **Pitch** — investor / partner walk-through
- **Product north star** — internal alignment artifact
- **Developer alignment artifact** — every contributor builds against
  the same loop
- **Onboarding animation** — first-run experience for new operators

**Do not render the clip in this proposal.** This proposal locks the
scene order, the scene contracts, and the example intent. The actual
cinematic rendering is a separate proposal-class artifact under
`docs/proposals/` (sibling) or a HyperFrames composition under
`oracle_town/skills/video/hyperframes/` (production layer) — neither
is in scope here.

When the clip is rendered, it must respect:
- the 8 scenes in §2 / §3 in order
- the example intent in §2 verbatim
- the receipt content in §3 Scene 5 verbatim
- the receipt class label in §3 Scene 7 verbatim
- the §5 hide-more rule
- the §10 non-goals

---

## §10. Non-Goals

This proposal does **not**:

- implement any window manager, route, or component
- build a GUI prototype
- render the cinematic clip
- modify the sovereign kernel, governance, schemas, ledger, closures,
  or tranche receipts
- promote any candidate to canon
- amend any sealed receipt or constitutional artifact
- script Temple Mode (sibling proposal does that)
- script Witness Mode in detail (covered by parent UX proposal §10)
- commit any change to git unless explicitly asked
- push any change to a remote unless explicitly asked

---

## §11. Final Receipt

```
authority:             NON_SOVEREIGN
canon:                 NO_SHIP
lifecycle:             PROPOSAL
implementation_scope:  INTERACTION_GRAMMAR_DOC_ONLY
implementation_status: NOT_IMPLEMENTED
commit_status:         NO_COMMIT (pending operator authorization)
push_status:           NO_PUSH  (pending operator authorization)
peer_review_required:  YES (Rule 3, Proposer ≠ Validator)
verdict_authority:     MAYOR (after operator countersignature)
next_verb:             review interaction grammar
```
