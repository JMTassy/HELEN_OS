# WARREN VOX — Scene Grammar

authority: false · claim: NO_CLAIM · paid_generation_calls: 0  
Render layer only. `scene grammar ↛ game mechanics`.

## One-line product

**One stage. One coach. One card. Three stamps. Always one obvious next click.**

## Layout contract (day family)

```
[ title · day/tag ]
[ meters × 3 ]                    optional but preferred
[ STAGE — garden plate ]          required for "alive"
[ COACH — names next click ]      required if interactive
[ PROPOSAL / CONTENT CARD ]       one idea at a time
[ STAMPS / VERBS — fat buttons ]  min-height 64px
[ short log ]                     optional
[ law footer ]                    required
```

Mobile: max-width ~520px centered. Touch targets ≥ 44px (prefer 52–64).

## First-click law (non-negotiable)

If a newcomer cannot find the first click in **2 seconds**, the surface fails VOX.

- Full-screen overlay + **one** primary button is legal.
- Keyboard-only primary loops are **illegal** (V2 anti-pattern).
- API-key walls before first play are **illegal**.

## Color law

| Token | Means on skin | Must NEVER mean |
|---|---|---|
| `--vox-admit` green | moss / Fix / grow stamp chrome | Kernel ADMITTED / sealed truth |
| `--vox-deny` red | block stamp | system crash only |
| `--vox-compost` brown | bury soft / soil | delete-from-ledger |
| `--vox-glow` orange | focus / active proposal | emergency / paid premium |
| `--vox-gold` | coach labels / day tags | money / ZOL authority |

Green-as-written is forbidden (HELEN WULMOJI). Footer must include:

```
Garden ADMIT ≠ Kernel ADMISSION · authority=false · VOX skin only
```

## Forbidden morphisms (from Garden Layer Grammar)

| Morphism | Why |
|---|---|
| `Gauge ↛ Metric` | meters are skin until pure `f(events)` |
| `GameReceipt ↛ LedgerFact` | game log ≠ kernel ledger |
| `Feeling ↛ Proof` | affect is signal |
| `Beauty ↛ Admission` | VOX never admits |
| `Skin apply ↛ Reducer edit` | apply command must refuse script/reducer mutation |

## Experience before terminology

Prefer:

- "The seedlings are dry." over "membraneStress++"
- "Stamp Grub's idea." over "emit SIGNAL_ROSE"
- "Garden mutated." over "zoneWeights recomputed"

Kernel jargon belongs in Kernel panels, never on the first screen.

## Families

| `data-vox` | When |
|---|---|
| `day` (default) | parchment play, operator calm, free graphics default |
| `night` | day1-style dark garden |
| `glow` | purple iPhone vault mood — optional alternate |

Mechanics must not branch on family. Family is pure CSS.

## Composition density

- Stage: 3–8 cutouts max before it becomes confetti
- One active proposal card at a time
- Coach line is a single imperative sentence
- No Three.js / WebGL as **entry** skin (may exist elsewhere; VOX day does not require it)

## Provenance of this grammar

Extracted from `v3-play.html`, `play.html`, `day1.html`, `GARDEN_LAYER_GRAMMAR.md`, `helen-free-graphics` skill — see `EXTRACTION_LEDGER.md`.
