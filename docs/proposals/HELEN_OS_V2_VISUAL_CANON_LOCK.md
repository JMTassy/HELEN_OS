# HELEN OS v2 — Visual Canon Lock (Proposal)

NO CLAIM — NO SHIP — PROPOSAL ONLY — CANDIDATE_VISUAL_CANON

```
artifact_type:         PROPOSAL_VISUAL_CANON_LOCK
proposal_id:           HELEN_OS_V2_VISUAL_CANON_LOCK
authority:             NON_SOVEREIGN
canon:                 NO_SHIP
lifecycle:             PROPOSAL
implementation_status: NOT_IMPLEMENTED
memory_class:          CANDIDATE_VISUAL_CANON
captured_on:           2026-04-27
captured_by:           operator (jeanmarie.tassy@uzik.com)
parent_proposal:       docs/proposals/HELEN_OS_V2_USER_CENTRIC_UX.md (v2)
sibling_proposals:     docs/proposals/FOCUS_MODE_TERMINAL_SPEC.md
                       docs/proposals/TEMPLE_MODE_VISUAL_BRIEF.md
related_memory:        project_helen_os_v2_product_model.md
                       feedback_helen_protagonist_not_hologram.md
                       feedback_operator_dashboard_contract.md
purpose:               consolidate every visual rule for HELEN OS v2's four
                       modes into one canonical reference, frozen for v2.
                       Any future v2 mockup must conform.
```

> **Core thesis (preserved)**
> HELEN OS should not show intelligence everywhere.
> It should make intelligence feel effortless.

> **Closing canon (full four-mode)**
> HELEN OS n'est pas un dashboard. C'est un espace de décision.
> Focus Mode aide l'utilisateur à agir.
> Witness Mode prouve que l'action était gouvernée.
> Oracle Mode explore le sens symbolique.
> Temple Mode compose le futur sans le shipper.

---

## §0. Stop-rule

This is a **canon lock proposal**. It does not implement a renderer, build
a GUI, or commit anything. It locks the visual rules for HELEN OS v2 so
that future mockups, prompts, and design reviews have one place to look.

Promotion to "frozen canon" requires:
1. operator countersignature
2. all four mode images rendered and accepted (Focus, Witness, Oracle,
   Temple) per their respective briefs
3. archive paths under `artifacts/visual_canon/` allocated by operator

Until then: this is a candidate canon. Mockups should still conform.

---

## §1. Scope

In scope:
- HELEN protagonist visual invariants (cross-mode)
- palette, typography, spacing rules (cross-mode)
- per-mode visual rules (Focus / Witness / Oracle / Temple)
- per-mode required labels and badges
- per-mode forbidden elements
- mode toggle visual rules
- acceptance checklist for any v2 mockup

Out of scope:
- implementation (renderer, components, GUI build)
- selection of image-generation tools or models
- video / animation rules (Focus has §6.5 voice meter only; full motion
  is a separate proposal)
- CONQUEST visual canon (related but parallel — see
  `feedback_helen_protagonist_not_hologram.md` §"CONQUEST GameMaster framing")

---

## §2. Cross-mode invariants (apply to ALL four modes)

### §2.1 HELEN protagonist canon

Source of truth: `feedback_helen_protagonist_not_hologram.md`.

- young woman, vivid **copper / red hair**
- **blue-grey eyes**, fair skin, soft expressive face
- calm intelligent presence
- premium cinematic manga-realistic beauty
- **black / gold** HELEN OS outfit or sovereign-tech armor (variant per mode)
- embodied, present, emotionally central
- **never** a generic blue AI hologram
- **never** a robot
- **never** abstract interface only — interface frames her, never replaces her
- the interface is *around* HELEN, not *instead of* her

Posture varies per mode (§3.x). Identity invariants do not.

### §2.2 Palette (cross-mode base)

| Color | Use |
|---|---|
| Dark graphite | Base / canvas |
| Soft violet | Primary accent |
| Warm amber | Receipts, ledger, presence highlights |
| Restrained cyan | Live channels, live-thinking indicators |
| Muted green | Verified idle states (kernel up, ledger valid, gate clear) |
| Red | **Reserved.** NO_SHIP / verdict threshold only. Never decorative. |

Mode-specific palette additions: Oracle adds gold and chakra-spectrum
(sacred-only); Temple adds amber draft-glow. Focus and Witness use the
base palette only.

### §2.3 Typography

- single display weight, single body weight
- large readable sans-serif
- restrained — no decorative type, no script faces, no all-caps display
- generous line-height
- minimum 14pt body equivalent in any mockup

### §2.4 Spacing

- **Spatial calm** — Apple-like negative space, generous margins
- few elements per surface
- never "wall of data"
- never permanent overlay grid
- never permanent telemetry frame

### §2.5 Brand rule

HELEN OS may be Apple-like in **calm and restraint**, but must **not**
clone:
- macOS dock (the module rail is HELEN's own)
- macOS window chrome (no traffic-light close/min/max)
- macOS icon style (HELEN icons are HELEN-original)
- macOS menu bar
- iOS / iPadOS sheet styles wholesale

The OS is HELEN-native — first-principles operating system for the AI
era — not a derivative.

### §2.6 Glass surfaces

- translucent overlays for sheets, pop-ins, side panels
- subtle depth, no skeuomorphism
- glass acceptable for module surfaces and confirmation prompts; never
  for the main HELEN core

### §2.7 Sacred geometry

- **ambient only** — barely-visible grid harmonics
- **never decorative overlay**
- **never claimed as authority**
- foreground sacred geometry (mandalas, chakra wheels) is **only**
  permitted in Oracle Mode (§3.3)

---

## §3. Per-mode visual canon

### §3.1 FOCUS MODE — visual rules

Source: parent §4, parent §11, terminal spec §2–§9.

| Element | Rule |
|---|---|
| Mode label | `[ FOCUS MODE ]` active in toggle, `WITNESS MODE` available |
| Top toggle | **Always visible.** `FOCUS MODE \| WITNESS MODE` only — Oracle/Temple never appear in this toggle. |
| HELEN posture | Calm, central, present. Working alongside the operator. |
| HELEN outfit | Black / gold sovereign-tech, restrained — workday variant |
| Intent line | Practical work intent, in operator language. Canonical example: *"Prepare my Q3 product strategy from notes, market research, and recent emails."* |
| Suggested actions | **Exactly three**, numbered or bulleted. Canonical example: Research competitors / Synthesize key patterns / Draft Q3 strategy. |
| Channels panel | Right side, small: Voice / Mail / Telegram / Browser-Research |
| Voice waveforms | Two subtle waveforms (operator + HELEN) — visible, not foregrounded. Terminal substitute: 4-cell block-meter. |
| Ledger pill | `Latest Receipt: <CLASS> · APPENDED · Expand Ledger` or `No new mutations · Last receipt <time>` |
| LEGORACLE pill | **Idle by default**: `Gate Clear · No Active Claim`. Verdicts only during active claim eval. |
| Module rail | HELEN-original (not macOS dock). AMP / Files / Internet / Notes / Calendar / Mail / Oracle / Settings — small, quiet, non-dominant. |
| Product tagline | `HELEN suggests. You decide. Everything is recorded.` — visible beneath suggested actions. |
| Sacred geometry | Ambient only, barely visible. **No chakra mandala in Focus.** |
| Witness preview card | Small card: "Advanced inspection: receipts, gates, claims, reducer, constitution." Button: "Switch to Witness Mode" |
| Footer canon | `HELEN OS n'est pas un dashboard. C'est un espace de décision.` |

**Forbidden in Focus**: SHIP_FORBIDDEN ambient, SHIP_AUTHORIZED ambient,
8D mystical context as system data, sacred vocabulary as authority,
foreground mandala, walls of metrics, dashboard overload, macOS chrome
clones.

### §3.2 WITNESS MODE — visual rules

Source: parent §10, parent §11, parent §12.

| Element | Rule |
|---|---|
| Mode label | `[ WITNESS MODE ]` active in toggle, `FOCUS MODE` available |
| Top toggle | Always visible (same as Focus) |
| HELEN posture | Watchful, witnessing. Less central — the operator is inspecting the system, HELEN is the witness. |
| HELEN outfit | Black / gold sovereign-tech, slightly more formal than Focus |
| Constitution phrase | Header: `HELEN sees. HELEN proposes. The gate authorizes. The executor acts. The ledger records. The reducer decides.` |
| Surfaces (left rail) | Receipt ledger / Claim workflow / Policy gates / Language firewall / Desire firewall / LEGORACLE / Reducer state / Ghost closure detector / Knowledge compiler / Constitutional strip / Worker lanes |
| Active claim verdicts | `SHIP_AUTHORIZED` / `SHIP_FORBIDDEN` / `DENIED` / `PENDING_RECEIPT` — **only** when a claim is under active evaluation, **only** in the claim workflow surface, **scoped to the active claim id** |
| Ledger | Full NDJSON tail, paginated, filterable |
| Closing canon | Witness Mode export footer: full four-mode closing canon |
| Sacred geometry | Ambient only. No mandala. |

**Forbidden in Witness**: ambient SHIP_FORBIDDEN (still — even here it's
scoped to active claim), foreground sacred geometry, mystical labels as
authority, macOS chrome clones.

### §3.3 ORACLE MODE — visual rules

Source: parent §2.3.3, parent §5, image-prompt directives 2026-04-27.

| Element | Rule |
|---|---|
| Mode label | `ORACLE MODE` active. Mode rail shows `FOCUS \| WITNESS \| ORACLE \| TEMPLE` with Oracle highlighted — **Oracle-internal rail only**, not the default OS toggle. |
| Authority label | `NON_SOVEREIGN · SACRED · AI-NATIVE` — **never** `SOVEREIGN` |
| Badge | `Symbolic metaphor · non-authoritative` — **mandatory, visible, non-negotiable** |
| Receipt status | `Canon: NO_SHIP`, `Authority: NON_SOVEREIGN`, receipt id visible |
| Mandala | Foreground sacred mandala / chakra-inspired cognitive map **permitted here only**. Layers: Transcendence Crown / Unity Soul / Wisdom Mind / Harmony Heart / Foundation Body / Flow Energy / Service Action / Integration Being |
| HELEN posture | Contemplative, oracular, gesturing toward the symbolic map |
| HELEN outfit | Black / gold with optional sacred-tech inflection (gold weighted heavier) |
| Three Oracle suggestions | Practical example: 1. Deepen knowledge lattice / 2. Stabilize field coherence / 3. Strengthen truth infrastructure |
| Footer | UX canon: `HELEN n'est pas un cockpit. HELEN est une présence calme qui ouvre le bon panneau au bon moment.` |
| Palette additions | Gold, chakra-spectrum (used **only** for sacred elements, never for system status) |
| Sacred vocabulary | Allowed **here only**, **always as metaphor** |

**Forbidden in Oracle**: the word `SOVEREIGN` anywhere, any technical
authority claim from sacred elements, leaking sacred elements into Focus
or Witness, macOS chrome clones.

### §3.4 TEMPLE MODE — visual rules

Source: parent §2.3.4, sibling `TEMPLE_MODE_VISUAL_BRIEF.md`.

| Element | Rule |
|---|---|
| Mode label | `TEMPLE MODE` active in Temple-internal mode rail |
| Mode rail context | Shown internally only — `FOCUS · WITNESS · ORACLE · TEMPLE` with Temple highlighted; never the default OS toggle |
| Authority labels | `NON_SOVEREIGN · NO_SHIP · DRAFT` — **never** `SOVEREIGN`, **never** `READY`, **never** `SHIP_AUTHORIZED` |
| Badge | `Symbolic drafting · Non-authoritative` — mandatory |
| HELEN posture | Contemplative, composing, drafting — gesturing softly toward a draft surface, sketching, writing |
| HELEN outfit | Black / gold sovereign-tech, premium and restrained (not armor) |
| Composition surface | Luminous draft surface (glass slate / holographic notebook) with **visibly incomplete** geometry forming. Incompleteness is intentional. |
| Sacred geometry | Ambient only — soft mandala echo deep in background. **No foreground mandala** (that's Oracle's). |
| Palette additions | Warm amber draft-glow on the composition surface |
| LEGORACLE | **No active claims by definition** — Temple is pre-claim. No verdict pill. |
| Footer | Closing canon: full four-mode block, including `Temple Mode compose le futur sans le shipper.` |
| Mood | Sanctuary, contemplation, quiet creative power |

**Forbidden in Temple**: the word `SOVEREIGN`, any ship/ready/deployed
verb, foreground mandala, cockpit / dashboard / metrics walls, generic
AI hologram, macOS chrome clones, bright red, mystical labels claimed as
authority.

---

## §4. Mode toggle visual rules

| Surface | Visible toggle |
|---|---|
| Default OS screen (Focus or Witness) | `[ FOCUS MODE ]  \|  WITNESS MODE` — only these two |
| Inside Oracle Mode | Oracle-internal mode rail showing all four (informational, not actionable across) — operator returns to default screen via close, then opens via dock again |
| Inside Temple Mode | Temple-internal mode rail showing all four (same pattern as Oracle) |
| Inside any module (AMP / Files / etc.) | No mode toggle — module surfaces own the body region; close returns to Focus |

**Hard rule** (parent §2.3.5, restated): Oracle and Temple **never** appear
in the default OS top toggle. They are reached only by opening the
corresponding dock module. This is what protects Focus and Witness from
sacred-vocabulary leakage.

---

## §5. Cross-mode forbidden list

These never appear in any v2 mockup, in any mode:

- generic blue AI hologram in HELEN's place
- HELEN as a robot
- HELEN as abstract interface only
- macOS dock clone, traffic-light window chrome, menu bar
- the word `SOVEREIGN` (HELEN OS v2 is `NON_SOVEREIGN` end-to-end at
  proposal stage)
- 8D mystical labels claimed as system authority outside Oracle (and
  inside Oracle only as metaphor with the badge)
- ambient SHIP_FORBIDDEN
- bright red as decoration (red is reserved for NO_SHIP / verdict
  threshold only)
- blinking text, marquee scroll, color cycling
- "AI thinking..." idle text or spinners longer than 1 line
- toasts that linger beyond ~3 seconds

---

## §6. Required labels per mode (matrix)

| Label | Focus | Witness | Oracle | Temple |
|---|---|---|---|---|
| `FOCUS MODE \| WITNESS MODE` toggle | ✓ | ✓ | — (internal rail) | — (internal rail) |
| Product tagline | ✓ | — | — | — |
| Constitution phrase header | — | ✓ | — | — |
| `Canon: NO_SHIP` | ✓ (in receipt sheet) | ✓ | ✓ (mandatory) | ✓ (mandatory) |
| `Authority: NON_SOVEREIGN` | (implied) | (implied) | ✓ (mandatory) | ✓ (mandatory) |
| `NON_SOVEREIGN · SACRED · AI-NATIVE` | — | — | ✓ | — |
| `Symbolic metaphor · non-authoritative` badge | — | — | ✓ | — |
| `Symbolic drafting · Non-authoritative` badge | — | — | — | ✓ |
| `NON_SOVEREIGN · NO_SHIP · DRAFT` pill | — | — | — | ✓ |
| LEGORACLE idle pill | ✓ | (or active verdict) | — | — |
| Closing canon (full 4-mode) | — | ✓ (export footer) | (Oracle uses UX canon footer) | ✓ (Temple uses sealing-phrase footer) |

---

## §7. Acceptance checklist (any v2 mockup, any mode)

- [ ] HELEN protagonist canon respected (§2.1)
- [ ] Palette conforms (§2.2)
- [ ] Typography conforms (§2.3)
- [ ] Spatial calm (§2.4)
- [ ] No macOS chrome clones (§2.5)
- [ ] Mode label correct for the mode being rendered (§3.x)
- [ ] Toggle rule respected (§4)
- [ ] No item from cross-mode forbidden list (§5)
- [ ] Required labels for the mode all present (§6)
- [ ] Sacred geometry: ambient in Focus/Witness/Temple, foreground only
      in Oracle (§2.7, §3.3)
- [ ] No `SOVEREIGN` text anywhere
- [ ] LEGORACLE state correct for context (idle by default; verdicts
      only with active claim)

If any checkbox fails: regenerate or amend the mockup before promotion.

---

## §8. References

- Parent: `docs/proposals/HELEN_OS_V2_USER_CENTRIC_UX.md` (v2)
- Sibling (terminal): `docs/proposals/FOCUS_MODE_TERMINAL_SPEC.md`
- Sibling (Temple): `docs/proposals/TEMPLE_MODE_VISUAL_BRIEF.md`
- Memory: `project_helen_os_v2_product_model.md`
- Memory: `feedback_helen_protagonist_not_hologram.md`
- Memory: `feedback_operator_dashboard_contract.md`
- Memory (related, ambient sacred geometry rule): `feedback_wulmoji_aura_temple.md`

---

## §9. Promotion path to frozen canon

1. Operator review of this proposal + parent + terminal spec + Temple brief
2. Render Focus / Witness / Oracle / Temple images per their briefs
3. Run §7 acceptance checklist on each
4. If all pass: allocate `artifacts/visual_canon/` paths
   (operator countersignature required)
5. Archive accepted images
6. Mark this proposal as `lifecycle: FROZEN_CANON_V2` (lifecycle change
   requires operator signature in a follow-up artifact)
7. Update memory `project_helen_os_v2_product_model.md` with frozen-canon
   image paths
8. Only then is the v2 visual canon "locked"

Until step 6, this is candidate canon. Conform to it for mockups; cite
this proposal in any visual review.

---

## §10. Final Receipt

```
authority:             NON_SOVEREIGN
canon:                 NO_SHIP
lifecycle:             PROPOSAL
implementation_scope:  VISUAL_CANON_LOCK_DRAFT_ONLY
implementation_status: NOT_IMPLEMENTED
commit_status:         NO_COMMIT
push_status:           NO_PUSH
parent_proposal:       HELEN_OS_V2_USER_CENTRIC_UX (v2)
sibling_proposals:     FOCUS_MODE_TERMINAL_SPEC, TEMPLE_MODE_VISUAL_BRIEF
next_verb:             review visual canon lock
```
