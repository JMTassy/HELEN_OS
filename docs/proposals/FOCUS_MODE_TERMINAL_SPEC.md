# FOCUS MODE — Terminal Spec (Proposal)

NO CLAIM — NO SHIP — PROPOSAL ONLY — CANDIDATE_SPEC

```
artifact_type:         PROPOSAL_SPEC_DRAFT
proposal_id:           FOCUS_MODE_TERMINAL_SPEC
authority:             NON_SOVEREIGN
canon:                 NO_SHIP
lifecycle:             PROPOSAL
implementation_status: NOT_IMPLEMENTED
memory_class:          CANDIDATE_SPEC
captured_on:           2026-04-27
captured_by:           operator (jeanmarie.tassy@uzik.com)
parent_proposal:       docs/proposals/HELEN_OS_V2_USER_CENTRIC_UX.md (v2)
related_memory:        project_helen_os_v2_product_model.md
                       feedback_helen_protagonist_not_hologram.md
                       feedback_operator_dashboard_contract.md
```

> **Core thesis (preserved from parent)**
> HELEN OS should not show intelligence everywhere.
> It should make intelligence feel effortless.

---

## §0. Stop-rule

This is a terminal-shape derivation of FOCUS MODE from the parent v2 UX
proposal. It defines a CLI rendering contract; it does **not** implement.
No code, no entrypoint, no commit, no push. Promotion to a buildable spec
requires operator countersignature **and** Option B (calm-mode toggle)
reconciliation in the parent proposal.

---

## §1. Scope

This spec covers **only** FOCUS MODE rendered in a terminal (TTY, ≥ 80
columns, monospace, ANSI 24-bit color preferred, ANSI 16-color fallback).

Out of scope (see §10):
- WITNESS MODE (separate spec)
- GUI rendering of any kind
- Voice waveforms (visual-only — see §6.5 for textual analog)
- Module internals (AMP, Files, etc. — addressed by per-module specs)
- Receipt schema (canonical: `helen_os/schemas/`)
- LEGORACLE evaluation logic (canonical: `helen_os/governance/`)

---

## §2. Frame layout (≥ 80 cols × ≥ 24 rows)

```
┌────────────────────────────────────────────────────────────────────┐
│ kernel ●  ledger ●  safety ●          [ FOCUS ] | witness          │ ← header (1 row)
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│  ◉ HELEN                                  channels                 │
│                                           voice    ●  zephyr       │ ← body
│  intent:                                  mail     2               │   (variable)
│    Prepare my Q3 product strategy from    telegram ●               │
│    notes, market research, and recent     browser  ●  research     │
│    emails.                                                         │
│                                                                    │
│  proposals:                                                        │
│    1  Research competitors                                         │
│    2  Synthesize key patterns                                      │
│    3  Draft Q3 strategy                                            │
│                                                                    │
│  HELEN suggests. You decide. Everything is recorded.               │ ← tagline
│                                                                    │
├────────────────────────────────────────────────────────────────────┤
│ ⏚ INTENT_UPDATED · APPENDED · :ledger to expand                    │ ← ledger pill
│ Gate Clear · No Active Claim                                       │ ← LEGORACLE
│ AMP  Files  Net  Notes  Cal  Mail  Oracle  Settings    :help       │ ← dock
└────────────────────────────────────────────────────────────────────┘
```

Three regions, separated by horizontal rules:

1. **Header** (1 row) — top status pills + mode toggle indicator.
2. **Body** (variable) — HELEN core glyph, intent, proposals, channels,
   product tagline.
3. **Footer** (3 rows) — ledger pill, LEGORACLE pill, dock.

Below ≥ 80 cols × ≥ 24 rows the renderer **must** degrade gracefully (§9),
not fail.

---

## §3. Header

```
kernel ●  ledger ●  safety ●          [ FOCUS ] | witness
```

| Element | Contract |
|---|---|
| `kernel ●` | dot color = kernel daemon health (green up / amber lag / red down) |
| `ledger ●` | dot color = ledger chain integrity (green valid / amber lag / red error) |
| `safety ●` | dot color = language + desire firewall (green clean / amber warning / red active block) |
| `[ FOCUS ]` | bracketed = active. Lowercase `witness` = available, inactive |

Status pills are **read-only** in Focus Mode. The operator opens any of
them with `:status <pill>` to see drill-down (e.g. `:status ledger` shows
the recent receipts sheet). Drilling deeper into a status pill flips to
WITNESS at that surface.

Mode toggle: `:witness` flips. Returning is `:focus` from inside Witness.

---

## §4. HELEN core glyph

The terminal cannot render the embodied protagonist canon visually. It
substitutes a **single calm presence glyph** at column 3 of the body's
first row:

```
◉ HELEN
```

- glyph: `◉` (filled medium circle, U+25C9)
- label: `HELEN` in default body color
- never animated, never spinning, never pulsing
- never substituted with `🤖`, `🧠`, `✨`, or any sacred/mystical glyph
- never preceded or followed by emoji unless the terminal is opt-ed into
  WULmoji mode in AURA / Temple — both confined to Oracle / Temple modules
  (see parent §2.5 hard rule)

The terminal renderer is responsible for protecting this glyph from
sacred-vocabulary leakage, not the operator.

---

## §5. Intent block

```
intent:
  <one-sentence intent in operator language, wrapped at body width - 4>
```

- exactly one intent at any time
- never collapses
- always visible while in Focus Mode body
- editable via `:intent <new intent>` (mutation — see §8)
- example (canon, from parent §4): *"Prepare my Q3 product strategy from
  notes, market research, and recent emails."*

Forbidden: mystical / 8D / sacred phrasings. The renderer **may** flag a
proposed intent that matches a configured sacred-vocabulary classifier,
but the verdict is the operator's.

---

## §6. Proposals block

```
proposals:
  1  <action label>
  2  <action label>
  3  <action label>
```

### §6.1 Hard rules

- **Maximum 3 proposals.** If the planner produces more, it has not yet
  understood the intent — the renderer truncates to 3 and surfaces the
  remainder via `:more` (Witness Mode only).
- **Numbered 1, 2, 3** — single digit + two-space gap.
- **Selection**: operator types `1`, `2`, or `3` and presses Enter.
- **Cancel**: operator types `:cancel` to clear proposals.

### §6.2 Selection → confirmation

Selecting a numbered proposal opens the **receipt confirmation prompt**
(§8). Selection alone does **not** mutate state.

### §6.3 Refresh

Proposals refresh:
- on `:intent <new intent>` (after the new intent is confirmed)
- on `:refresh proposals` (no mutation, regenerate from current intent)
- on receipt of an explicit replanning event from the kernel

Proposals **do not** refresh ambient. The Focus surface stays still.

### §6.4 Channels panel

Right-aligned in the body, vertically centered to the proposals block:

```
channels
voice    ●  zephyr
mail     2
telegram ●
browser  ●  research
```

- presence dot or count per channel
- compact: at most 4 channels
- non-blocking — never steals input focus
- if a channel maps to a dock module currently in use, the channel line
  shows a `→` instead of a presence dot

### §6.5 Voice waveform — terminal substitute

The parent §4 visual spec includes two subtle waveforms (operator + HELEN
voice). The terminal renders this as a **single one-character meter** in
the channels panel `voice` line:

```
voice    ●  zephyr   ▁▂▂▁
```

- 4-cell block-meter, updates ≤ 5 Hz
- when no audio: line collapses to `voice    ●  zephyr` (no meter)
- never blinks, never colored red

This is the only animated element in Focus Mode body, and it is opt-in
via `:settings voice meter on`.

---

## §7. Product tagline

```
HELEN suggests. You decide. Everything is recorded.
```

- always rendered immediately below the proposals block
- one line, body color, no decoration
- never paraphrased, never split across lines
- if body width forces wrapping, the tagline is the last element kept (the
  channels panel collapses first — see §9)

---

## §8. Receipt confirmation prompt (mutation gate)

When a proposal is selected, **before** any kernel route is invoked, the
renderer shows:

```
HELEN proposes:
  <one-sentence summary of what will happen>

  → kernel route   : <op>
  → expected receipt: <RECEIPT_CLASS_V1>
  → inputs (▾ to expand)

  [ y ]es   [ n ]o   [ i ]nputs
```

- single-key answer, case-insensitive
- `y` → kernel route invoked → on success, receipt hash flashes in ledger
  pill for ~3 seconds → return to Focus body
- `n` → prompt dismissed, nothing routed, return to Focus body
- `i` → expands `inputs` block in-place; prompt remains, awaiting `y`/`n`

This is the **only** path through which a Focus Mode action enters the
spine. No silent mutation.

---

## §9. Footer

### §9.1 Ledger pill

```
⏚ <RECEIPT_CLASS> · <STATUS> · :ledger to expand
```

- single line, never wraps
- `<RECEIPT_CLASS>` = most recent receipt class (e.g. `INTENT_UPDATED`)
- `<STATUS>` = `APPENDED` / `PENDING` / `ERROR`
- `:ledger` opens the recent-receipts sheet (last N, default 10)
- `:ledger full` flips to WITNESS Mode at the ledger surface

### §9.2 LEGORACLE pill

```
Gate Clear · No Active Claim                       (idle, default)
```

During active claim evaluation **only**, the line becomes one of:

```
PENDING_RECEIPT · <claim_id> · :claim to inspect
SHIP_AUTHORIZED · <claim_id> · :claim to inspect
SHIP_FORBIDDEN · <claim_id> · :claim to inspect
DENIED · <claim_id> · :claim to inspect
```

**Hard rule** (parent §2.4): `SHIP_FORBIDDEN` must **not** appear when no
claim is under evaluation. The renderer enforces this — if the kernel
emits a stale verdict with no active claim, the renderer falls back to
idle and logs the inconsistency to Witness Mode's `claim workflow`.

### §9.3 Dock

```
AMP  Files  Net  Notes  Cal  Mail  Oracle  Settings    :help
```

- single line, lowercase mnemonic for command access
- `:amp`, `:files`, `:net`, `:notes`, `:cal`, `:mail`, `:oracle`,
  `:settings` open the corresponding module
- modules render as **takeover sheets** (full body region replaced); on
  exit, Focus body is restored exactly
- `:help` shows command reference
- the dock line is the only place where a module name is rendered in
  Focus; once opened, the module owns the body region

---

## §10. Degradation rules (narrow / non-color terminals)

| Terminal capability | Behavior |
|---|---|
| < 80 cols | Channels panel collapses (drop §6.4). Tagline kept. Proposals kept. |
| < 60 cols | Drop `kernel/ledger/safety` labels in header — keep dots only. |
| < 40 cols | **Refuse to start in Focus Mode.** Render: `HELEN OS requires ≥ 40 cols. Resize and retry.` Do not degrade further — calm requires space. |
| No 24-bit color | Use ANSI 16-color: green/yellow/red dots, white text. |
| No color at all | Use Unicode shape: `●` valid, `◐` warning, `○` error. |
| No Unicode | Use ASCII: `*` valid, `~` warning, `!` error. HELEN glyph becomes `[H]`. |

The renderer never silently corrupts a calm surface. If it cannot meet the
calm contract, it refuses and explains why.

---

## §11. Forbidden in Focus Mode terminal

- ambient `SHIP_FORBIDDEN` line (§9.2 hard rule)
- ambient `SHIP_AUTHORIZED` line (only during active claim eval)
- 8D / mystical / sacred labels as system text
- WULmoji or sacred glyphs adjacent to HELEN core or kernel/ledger/safety
  pills (per `feedback_wulmoji_aura_temple.md` — confined to AURA/TEMPLE)
- blinking text, marquee scroll, color cycling
- spinners, progress bars longer than 1 line, "AI thinking..." idle text
- toasts that linger beyond ~3 seconds
- more than 3 proposals
- any element that animates without an opt-in setting (§6.5 is the only
  exception, opt-in)

---

## §12. Open questions for parent reconciliation

1. **Channels panel ↔ dock module overlap** — when `:mail` is open, does
   the channels panel still show `mail 2`? Proposed: yes, with `→` marker
   (§6.4); operator confirmation needed.
2. **Witness drill-down depth** — does `:status ledger` flip to Witness
   immediately, or open a Focus-side sheet first? Proposed: Focus-side
   sheet first, second drill-down flips. Parent §8 deep-link should be
   tightened.
3. **Voice meter default** — opt-in (§6.5) or opt-out? Proposed: opt-in
   to preserve calm contract.
4. **Sacred-vocabulary classifier in §5** — does the renderer warn or stay
   silent on a sacred-flavored intent? Proposed: silent in Focus, only
   surface in Witness `language firewall`.

---

## §13. Non-Goals

This spec does **not**:

- implement the renderer
- specify the kernel API surface (canonical: `helen_os/governance/`,
  `tools/helen_say.py`)
- specify the input parser / command grammar beyond the colon-prefixed
  command shapes shown
- specify the receipt schema (canonical: `helen_os/schemas/`)
- specify Witness Mode terminal layout (separate spec)
- promote this candidate to canon
- commit any change to git
- push any change to a remote

---

## §14. Final Receipt

```
authority:             NON_SOVEREIGN
canon:                 NO_SHIP
lifecycle:             PROPOSAL
implementation_scope:  TERMINAL_SPEC_DRAFT_ONLY
implementation_status: NOT_IMPLEMENTED
commit_status:         NO_COMMIT
push_status:           NO_PUSH
parent_proposal:       HELEN_OS_V2_USER_CENTRIC_UX (v2)
next_verb:             review terminal spec
```
