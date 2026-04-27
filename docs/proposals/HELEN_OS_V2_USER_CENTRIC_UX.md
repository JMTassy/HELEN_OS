# HELEN OS v2 — User-Centric UX (Proposal)

NO CLAIM — NO SHIP — PROPOSAL ONLY — CANDIDATE_UX

```
artifact_type:         PROPOSAL_UX_DRAFT
proposal_id:           HELEN_OS_V2_USER_CENTRIC_UX
authority:             NON_SOVEREIGN
canon:                 NO_SHIP
lifecycle:             PROPOSAL
implementation_status: NOT_IMPLEMENTED
memory_class:          CANDIDATE_UX
captured_on:           2026-04-27
captured_by:           operator (jeanmarie.tassy@uzik.com)
revision:              v2 (two-mode product resolution + LEGORACLE state
                       contract + CONTEXT STACK grounding)
provenance:            operator UX redirection 2026-04-27 (initial),
                       operator product resolution 2026-04-27 (two-mode model,
                       grounded intent, anti-mystical correction).
related_memory:        feedback_operator_dashboard_contract.md
                       project_helen_amp.md
                       feedback_helen_protagonist_not_hologram.md
```

> **Product tagline**
> HELEN suggests. You decide. Everything is recorded.

> **Core thesis (preserved)**
> HELEN OS should not show intelligence everywhere.
> It should make intelligence feel effortless.

> **UX canon (preserved)**
> HELEN n'est pas un cockpit.
> HELEN est une présence calme qui ouvre le bon panneau au bon moment.

> **Closing canon**
> HELEN OS n'est pas un dashboard. C'est un espace de décision.
> Focus Mode aide l'utilisateur à agir.
> Witness Mode prouve que l'action était gouvernée.
> Oracle Mode explore le sens symbolique.
> Temple Mode compose le futur sans le shipper.

---

## §1. Executive Summary

HELEN OS v2 is a single AI-native operating system surfaced through **two
clearly named modes**:

- **FOCUS MODE** — default. Daily-use surface. Calm, contextual, one active
  intent, three suggested actions. The intelligence is felt, not displayed.
- **WITNESS MODE** — advanced. Constitutional inspection surface. Full
  receipt ledger, claim workflow, policy gates, LEGORACLE verdicts, reducer
  state. Operators reach this only when watching the system, not when
  working.

The constitutional spine — sovereign kernel, append-only ledger, K-gate
discipline, NO RECEIPT = NO CLAIM — is unchanged. What changes is **what is
shown by default**. Capacity meters, OS noise, gate verdicts, raw ledger
tail move to Witness Mode behind a single mode toggle.

The two modes are first-class. Focus Mode helps the user **act**. Witness
Mode proves the action was **governed**.

This document is a **design proposal only**. It does not implement, does not
ship, does not amend any constitutional contract. See §13 for non-goals.

---

## §2. Two Modes — Product Resolution

```
┌──────────────────────────────────────────────────────────┐
│   [ FOCUS MODE ] | [ WITNESS MODE ]                      │  ← top toggle
└──────────────────────────────────────────────────────────┘
```

### §2.1 FOCUS MODE (default)

The surface for **working**.

- one active intent (in the operator's language)
- three suggested actions, maximum
- compact ledger pill (dot + count)
- LEGORACLE in **idle state**: `Gate Clear · No Active Claim`
- modules hidden until invoked
- operator voice + HELEN voice visible but subtle (two small waveforms)
- right-side **contextual channels panel** (Voice / Mail / Telegram /
  Browser-Research) — small, non-blocking
- no permanent telemetry overlay
- no permanent gate verdict banner
- no permanent claim status

This is what 99% of sessions see, 100% of the time.

### §2.2 WITNESS MODE (advanced inspection)

The surface for **watching the system**.

- full receipt ledger (raw NDJSON tail, paginated)
- claim workflow (active claims, history, evaluator pipeline)
- policy gates (K8 / K-tau / K-rho / K-wul status, last verdicts, run logs)
- language firewall (active classifiers, recent blocks)
- desire firewall (active classifiers, recent blocks)
- LEGORACLE verdicts (active claim evaluation surface)
- reducer state (skill promotion reducer, bridge classifier outputs)
- ghost closure detector
- knowledge compiler (corpus state, T4/T6 floor outputs)
- constitutional strip (kernel boot manifest, mayor key registry, schema
  registry status)
- worker lanes (`ops/runs/<run-id>/workers/...`)

Witness Mode is reached via the top toggle or from a deep-link in the ledger
pill. It is never auto-opened by the system.

### §2.3 Four-Mode Product Map

The OS recognizes four operator stances. **Only Focus and Witness ship as
top-level product modes** with the visible toggle on the default screen.
Oracle and Temple ship as **dock modules**, not as default OS surfaces.

| Mode | Stance | Surface | Top toggle? |
|---|---|---|---|
| **FOCUS** | "I am working." | Default screen | yes (`[ FOCUS ]` active) |
| **WITNESS** | "I am watching the system." | Top toggle → constitutional dashboard | yes |
| **ORACLE** | "I am exploring symbolic meaning." | Dock module, pop-in card | no |
| **TEMPLE** | "I am composing / reflecting / imagining." | Dock module, side panel | no |

#### §2.3.1 FOCUS MODE

- default daily-use interface
- **practical work intents only** (no mystical / 8D / sacred phrasings)
- one active intent at any time
- **three suggested actions, maximum**
- compact ledger pill
- LEGORACLE quiet idle state: `Gate Clear · No Active Claim`
- modules hidden until invoked
- canonical example intent: *"Prepare my Q3 product strategy from notes,
  market research, and recent emails."*

#### §2.3.2 WITNESS MODE

- advanced inspection surface
- full receipt ledger (raw NDJSON tail, paginated)
- claim workflow (active claims, evaluator pipeline, history)
- policy gates (K8 / K-tau / K-rho / K-wul)
- language firewall (active classifiers, recent blocks)
- desire firewall (active classifiers, recent blocks)
- LEGORACLE verdicts (`SHIP_AUTHORIZED` / `SHIP_FORBIDDEN` / `DENIED` /
  `PENDING_RECEIPT`) — surfaced **only during active claim evaluation**
- reducer state (skill promotion reducer, bridge classifier outputs)
- ghost closure detector
- knowledge compiler (corpus state, T4/T6 floor outputs)
- constitutional strip (kernel boot manifest, mayor key registry, schema
  registry status)

#### §2.3.3 ORACLE MODE

- **symbolic interpretation mode** — opened from the dock, not the toggle
- AURA maps allowed
- mandalas / chakras / archetypes allowed
- sacred vocabulary allowed **only as metaphor**
- every Oracle surface **must** display the badge:
  `Symbolic metaphor · non-authoritative`
- authority label on every Oracle artifact: `NON_SOVEREIGN · SACRED ·
  AI-NATIVE` — never `SOVEREIGN`
- canon-bearing receipt status visible: `Canon: NO_SHIP`,
  `Authority: NON_SOVEREIGN`
- never claims technical authority
- never leaks into Focus or Witness surfaces

#### §2.3.4 TEMPLE MODE

- creation, reflection, composition, design **sanctuary**
- imagination and symbolic drafting allowed
- no implementation without receipt
- no commit
- no push
- `NON_SOVEREIGN` / `NO_SHIP` remains active for every Temple artifact
- currently unrendered (no canonical Temple visual surface yet)

#### §2.3.5 Cross-mode rule

The `FOCUS MODE | WITNESS MODE` toggle is **always visible on the default
screen** and **only those two modes appear in the toggle**. Oracle and
Temple are **never** in the top-level toggle — they open from the dock as
modules. This prevents sacred vocabulary from leaking into the technical
surfaces of Focus or Witness.

### §2.4 LEGORACLE state contract

LEGORACLE is the gate that authorizes SHIP / NO_SHIP for an active claim.
**LEGORACLE has an idle state.**

| State | When it appears | Where it appears |
|---|---|---|
| `Gate Clear · No Active Claim` | default, no claim under evaluation | Focus Mode, quiet pill |
| `PENDING_RECEIPT` | claim active, awaiting evidence | claim workflow surface |
| `SHIP_AUTHORIZED` | LEGORACLE evaluated → SHIP | claim workflow surface |
| `SHIP_FORBIDDEN` | LEGORACLE evaluated → NO_SHIP | claim workflow surface |
| `DENIED` | claim rejected at policy gate | claim workflow surface |

**Hard rule**: `SHIP_FORBIDDEN` must **not** appear as a permanent
background status anywhere in the OS. It is a verdict on a specific claim,
during a specific evaluation window, surfaced only in the claim workflow.
Surfacing it ambient teaches the operator that HELEN refuses by default —
which is the opposite of the truth.

### §2.5 Context maps

There is one technical default and one symbolic alternate. They must not be
confused.

- **CONTEXT STACK** (technical default, used in Focus + Witness)
  Layers, in order:
  1. User Intent
  2. Active Task
  3. Files / Sources
  4. Memory Candidates
  5. Claims
  6. Policies
  7. Receipts
  8. Execution State

- **AURA CONTEXT MAP** (symbolic, **non-authoritative**, Oracle/Temple only)
  Metaphorical layering for symbolic exploration. Never appears in Focus or
  Witness. Never reads as system data.

**Hard rule**: sacred vocabulary (AURA, WULmoji, sacred geometry as
authority, mystical "8D" framings) must **not** appear as technical fact in
Focus or Witness. If it appears, it must be explicitly labeled `symbolic`
and confined to Oracle / Temple modules.

---

## §3. UX Principles

```
Voir moins.       See less.
Comprendre plus.  Understand more.
Agir plus vite.   Act faster.
```

Three operational consequences:

1. **Calm by default.** The Focus surface is sparse. Density is opt-in via
   the WITNESS toggle, not default.
2. **Intent-first.** The operator's current intent is the anchor. Every
   element on screen relates to that intent or it does not appear.
3. **Suggestion, not decision.** HELEN proposes; the user confirms; the
   ledger remembers. HELEN never decides silently.

---

## §4. Main Screen Structure (Focus Mode)

A calm surface. Five core elements + small contextual channels panel + mode
toggle. Nothing else is permanently visible.

```
┌──────────────────────────────────────────────────────────────────┐
│ [status: kernel · ledger · safety]  [ FOCUS | WITNESS ]          │
│                                                                  │
│                                                  ┌─────────────┐ │
│              ◉ HELEN Intelligence Core           │  Channels   │ │
│                                                  │  Voice ●    │ │
│              Current intent:                     │  Mail 2     │ │
│              "Prepare my Q3 product strategy     │  Telegram ● │ │
│               from notes, market research,       │  Browser ●  │ │
│               and recent emails."                │             │ │
│                                                  └─────────────┘ │
│              ▸ Research competitors                              │
│              ▸ Synthesize key patterns                           │
│              ▸ Draft Q3 strategy                                 │
│                                                                  │
│   〜〜  operator voice    HELEN voice  〜〜                       │
│                                                                  │
│                                          [⏚ ledger •••]          │
│                                                                  │
│   [ AMP ] [ Files ] [ Net ] [ Notes ] [ Cal ] [ … ]              │
└──────────────────────────────────────────────────────────────────┘
```

| Element | Contract |
|---|---|
| Mode toggle | `FOCUS | WITNESS` — top, always visible. Default Focus. |
| Top status pill | Kernel up/down, ledger health, safety state. No actions. |
| HELEN core | Embodied protagonist (canon `feedback_helen_protagonist_not_hologram.md`). Calm, central. Never a generic AI hologram. |
| Current intent | Grounded, operator-language. Example: *"Prepare my Q3 product strategy from notes, market research, and recent emails."* Never collapses. |
| Suggested actions | **Maximum 3.** Example shown: Research competitors / Synthesize key patterns / Draft Q3 strategy. |
| Channels panel (right) | Voice (Zephyr live), Mail (count), Telegram (presence), Browser-Research (active). Small, non-blocking. |
| Voice waveforms | Two subtle waveforms — operator input + HELEN output. Visible but not foregrounded. |
| Ledger pill | `Latest Receipt: INTENT_UPDATED · APPENDED · Expand Ledger`. Tap → sheet. Never a wall. |
| Dock | AMP / Files / Internet / Notes / Calendar / Mail / Oracle / Settings. Closed by default. |

**Forbidden in Focus Mode**: SHIP_FORBIDDEN banner, SHIP_AUTHORIZED banner
(unless an active claim is under evaluation), 8D mystical context, sacred
vocabulary as system authority.

---

## §5. Hidden Modules by Default

```
AMP    Files    Internet    Notes    Calendar    Mail    Oracle    Settings
```

Each module appears only when invoked. Closing returns to Focus Mode.

| Module | Surface form | Notes |
|---|---|---|
| AMP | Side panel (right) | Operator's resonance engine; canon `project_helen_amp.md` |
| Files | Sheet | Browse, scope-locked |
| Internet | Pop-in card | Search/fetch; receipt-bound if mutating |
| Notes | Side panel (left) | Capture surface |
| Calendar | Sheet | Read-first; mutations confirmed |
| Mail | Sheet | Read-first; mutations confirmed |
| Oracle | Pop-in card | Symbolic exploration. Sacred vocabulary allowed **here only**. Non-authoritative. |
| Settings | Sheet | Witness Mode opt-in toggle, language/desire firewall config |

---

## §6. Interaction Flow

```
clic / commande / voix
   → pop-in contextuel
   → choix simple (≤ 3 options)
   → receipt si mutation
   → retour au calme (Focus Mode)
```

Every path terminates in **return to calm** (Focus Mode). Voice and
command-line inputs collapse to the same flow as click.

---

## §7. Apple-like Behavior Rules

1. **One focus at a time.** Focus Mode has one anchor: current intent.
2. **Progressive disclosure.** Detail appears when asked for, never before.
3. **Soft panels, not walls of data.** Glass, spacing, restraint.
4. **Dropdowns** for choice, not always-rendered grids.
5. **Pop-ins are short.** Long sheets are split or paginated.
6. **No permanent chaos dashboard.** The cockpit (Witness Mode) is opt-in.
7. **Human intent is always visible** in Focus Mode.
8. **HELEN suggests; user confirms.** No silent mutation, ever.
9. **Ledger is compact, expandable.** Pill in Focus; full tail in Witness.
10. **Witness Mode is opt-in.** Power users find the toggle; novices stay in
    Focus and are protected.

---

## §8. Ledger UX

The ledger is **the constitutional spine**. In Focus Mode it is a single
pill. In Witness Mode it is the full tail.

**Focus Mode pill:**

```
[⏚ Latest Receipt: INTENT_UPDATED · APPENDED · Expand Ledger]
```

- dot color encodes ledger health (green = chain valid, amber = lag, red =
  integrity error)
- "Expand Ledger" → opens recent-receipts sheet (last N)
- a deeper drill-down link inside that sheet → flips the OS into Witness
  Mode at the ledger surface

**Witness Mode tail:**

- raw NDJSON, paginated
- filterable by op, receipt class, time
- export to file (read-only)

The ledger never blocks the main screen. **Quiet by default, expandable on
demand, never silenced.**

---

## §9. Receipt Confirmation Sheet

When an action mutates state, a small confirmation sheet shows:

```
┌──────────────────────────────────────────────┐
│  HELEN proposes:                             │
│  <one sentence — what will happen>           │
│                                              │
│  ▾ Inputs (collapsed)                        │
│  → kernel route: <op>                        │
│  → expected receipt: <RECEIPT_CLASS_V1>      │
│                                              │
│         [ Cancel ]      [ Confirm ]          │
└──────────────────────────────────────────────┘
```

After **Confirm**: receipt hash flashes in the ledger pill (~3s); surface
returns to Focus. After **Cancel**: sheet dismisses; nothing routed.

This is the only path through which mutation enters the spine from the UI.

---

## §10. Witness Mode (Advanced Inspection)

Hidden by default. Reached via the top mode toggle (`FOCUS | WITNESS`) or
from a deep-link in the ledger pill. Never auto-opened.

### §10.1 Surfaces

Each surface is its own panel, navigable from a left rail. They are not
shown simultaneously by default.

- **Receipt ledger** — full NDJSON tail, paginated, filterable
- **Claim workflow** — active claims, evaluator pipeline, history. This is
  where SHIP_AUTHORIZED / SHIP_FORBIDDEN / DENIED / PENDING_RECEIPT verdicts
  surface, **scoped to the active claim only**
- **Policy gates** — K8, K-tau, K-rho, K-wul status, last verdicts, run logs
- **Language firewall** — classifier state, recent blocks
- **Desire firewall** — classifier state, recent blocks
- **LEGORACLE** — active claim evaluation surface (idle when no claim)
- **Reducer state** — skill promotion reducer outputs, bridge classifier
- **Ghost closure detector** — `GOVERNANCE/CLOSURES/` integrity scan
- **Knowledge compiler** — corpus state, T4 (provenance) / T6 (intensity)
  floor outputs
- **Constitutional strip** — kernel boot manifest, mayor key registry,
  schema registry status
- **Worker lanes** — `ops/runs/<run-id>/workers/<agent>_<machine>/` trees

### §10.2 Witness Mode does not break Focus

The mode toggle is reversible at all times. State held in Witness panels is
view-only (no inadvertent mutation). The operator returns to Focus Mode by
flipping the toggle back.

### §10.3 Reconciliation with the dashboard contract

The operator dashboard contract (memory:
`feedback_operator_dashboard_contract.md`) requires capacity-visible and
OS-noise-exposed. Witness Mode satisfies "available without lying" but
defers always-on visibility. Reconciliation candidates:

| Option | Meaning |
|---|---|
| **A.** Status-pill compromise | Capacity + OS noise reduced to a top-bar pill in Focus; full surfaces in Witness. |
| **B.** Calm-mode toggle | Calm and full-cockpit are both first-class — exactly the two-mode model proposed here. |
| **C.** Amend the contract | "Visible" → "available on demand." |
| **D.** Reject this proposal | Keep cockpit-shaped HELEN OS. |

This proposal is a **realization of Option B**. Operator must countersign.

---

## §11. Visual Language

- **AI-native OS**, not an Apple clone. First-principles operating system
  for the AI era.
- **Brand rule.** HELEN OS may be Apple-like in **calm and restraint**, but
  must **not clone macOS chrome, dock, icon style, or menu bar**. The
  module rail at the bottom is HELEN's own design language, not a macOS
  dock. Window chrome, close/minimize/maximize affordances, and the top
  status row are HELEN-original, not Aqua/Sequoia mimicry.
- **Spatial calm.** Generous margins, few elements per surface.
- **Palette.** Dark graphite base · soft violet accents · warm amber for
  presence · restrained cyan for live channels · red reserved for
  NO_SHIP / verdict threshold.
- **Typography.** Large, readable, restrained. One display weight, one body
  weight.
- **Glass surfaces.** Translucent overlays for sheets and pop-ins.
- **Sacred geometry.** Quiet, ambient only — barely-visible grid harmonics.
  Never decorative overlay. Never claimed as authority.
- **HELEN protagonist canon** (`feedback_helen_protagonist_not_hologram.md`):
  copper / red hair, blue-grey eyes, fair skin, black/gold sovereign-tech
  outfit. Embodied, present, calm. **Not** a generic blue AI hologram. **Not**
  a robot.
- **Forbidden:** walls of charts, permanent telemetry overlays, blinking
  alerts, permanent SHIP_FORBIDDEN background, mystical "8D" overlays
  presented as system data.

---

## §12. Core Copy

### §12.1 Product tagline (top of every Focus surface)

```
HELEN suggests. You decide. Everything is recorded.
```

### §12.2 Constitution phrase (Witness Mode header)

```
HELEN sees.
HELEN proposes.
The gate authorizes.
The executor acts.
The ledger records.
The reducer decides.
```

### §12.3 UX canon (preserved as block, never paraphrased)

> HELEN n'est pas un cockpit.
> HELEN est une présence calme qui ouvre le bon panneau au bon moment.

### §12.4 Core thesis (preamble of every spec derived from this proposal)

> HELEN OS should not show intelligence everywhere.
> It should make intelligence feel effortless.

### §12.5 Closing canon (footer of every Witness Mode export)

> HELEN OS n'est pas un dashboard. C'est un espace de décision.
> Focus Mode aide l'utilisateur à agir.
> Witness Mode prouve que l'action était gouvernée.
> Oracle Mode explore le sens symbolique.
> Temple Mode compose le futur sans le shipper.

### §12.6 Phrase placement map

| Phrase | Where |
|---|---|
| Product tagline (§12.1) | Focus Mode, beneath suggested actions |
| Constitution phrase (§12.2) | Witness Mode header |
| UX canon (§12.3) | Internal docs, this proposal, design reviews |
| Core thesis (§12.4) | Preamble of any derived spec |
| Closing canon (§12.5) | Witness Mode export footer |

---

## §13. Non-Goals

This proposal does **not**:

- implement any window manager, route, or component
- build a GUI prototype
- modify the sovereign kernel, governance, schemas, ledger, closures, or
  tranche receipts
- amend the operator dashboard contract — it proposes Option B
  (calm-mode toggle) as reconciliation; operator must countersign
- promote any candidate to canon
- commit any change to git
- push any change to a remote
- claim mystical / sacred / 8D framings as technical authority anywhere
  in Focus or Witness
- show SHIP_FORBIDDEN as permanent background status anywhere

---

## §14. Final Receipt

```
authority:             NON_SOVEREIGN
canon:                 NO_SHIP
lifecycle:             PROPOSAL
implementation_scope:  UX_DESIGN_DOC_UPDATE_ONLY
implementation_status: NOT_IMPLEMENTED
commit_status:         NO_COMMIT
push_status:           NO_PUSH
next_verb:             review UX proposal
```
