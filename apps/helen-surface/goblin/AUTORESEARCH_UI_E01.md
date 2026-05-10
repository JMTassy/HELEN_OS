# AUTORESEARCH_UI_E01

**Status:** IN_FLIGHT  
**Class:** NON_SOVEREIGN  
**Authority:** false  
**Canon:** NO_SHIP  
**Date:** 2026-05-10  
**Operator:** JM Tassy  

---

## Mission

Find the **9.1/10 evolution** of the HELEN OS sovereign cockpit.

Baseline:
- Gravure (`goblin/gravure.html`) — operator rated **9/10** · "arty even if I do not understand"
- Cockpit (`index.html`) — currently rated below gravure · "backoffice" (pre-v3)

The target is not a higher score on a different artifact. It is the **cockpit itself reaching gravure-level presence**.

---

## Hypothesis E01

**H01 — Sacred Geometry Foundation**

> Embedding the gravure's sacred geometry layer as a permanent low-opacity background (7–13% breathing) in the cockpit creates pre-cognitive presence without compromising readability.

The claim: the cockpit IS the temple. When the geometry is visible at 7%, the operator's nervous system reads "sacred space" before cognition reads "interface." The same pre-cognitive hit that made the gravure 9/10 now underlies the productive surface.

---

## Experiment

**Mutation applied to:** `apps/helen-surface/index.html`

- `#geo-bg` SVG layer — `position:fixed; z-index:0; pointer-events:none`
- SVG breathing animation: opacity 7% → 13% over 14s
- Contents: Sri Yantra (9 triangles gold+red) · Flower of Life (7 circles) · Metatron spine axis · Rosicrucian cross (col 1) · Dharma wheel (col 2) · Templar cross (col 5) · Eye of Providence (header) · 4 corner pentagrams · VITRIOL + Hermetic margin text
- `.col-compass` background: `rgba(7,7,10,.15)` — geometry bleeds strongest through center column
- `#entry` background: `rgba(7,7,10,.96)` — geometry faintly present at state selection screen

**Structural alignment:** the column pillar lines in the SVG are aligned to the cockpit grid (x=200 / 400 / 840 / 1056). The cockpit structure IS the temple pillars.

---

## Metric

- Target: operator visual rating **≥ 9.1/10**
- Signal: "presence without clutter" / "feels alive" / "I'm inside it"
- Anti-signal: "too busy" / "distracting" / "can't read the text"

---

## Falsification Test

> "Look at the cockpit for 10 seconds. Does the sacred geometry background make it feel MORE like a sovereign presence, or does it feel visually cluttered?"

If answer = cluttered → H01 REJECTED. Revert mutation. Open E02.

---

## Supervision Protocol

1. Operator rates result in browser  
2. If **≥ 9.1**: KEEP · receipt_hash = commit SHA · open E02  
3. If **< 9.0**: REJECT · `git revert` · new hypothesis for E02  
4. If **= 9.0**: keep but iterate (E02 refines opacity / element selection)  
5. **No auto-promotion. No self-SHIP. Operator is MAYOR.**

---

## Receipt (pending)

```json
{
  "epoch": "AUTORESEARCH_UI_E01",
  "hypothesis": "sacred_geometry_foundation",
  "mutation_file": "apps/helen-surface/index.html",
  "mutation_type": "background_layer_addition",
  "baseline_rating": "9/10 gravure · backoffice cockpit",
  "metric_target": ">=9.1/10",
  "operator_rating": null,
  "verdict": "PENDING_OPERATOR_RATING",
  "receipt_hash": null,
  "commit": null
}
```

---

## E02 Hypotheses (pre-loaded, pending E01 result)

- **H02 — Radial State Selector:** Surface 0 mood cards as 8-point radial compass instead of 4x2 grid
- **H03 — Dark Cockpit Mode:** All columns fade to near-invisible when no active claim; only state badge + bindu persist
- **H04 — Moment Surface:** Remove 5-column layout; replace center with single "one thing at a time" surface
- **H05 — Typographic Temple:** Replace all labels with alchemical/sacred symbols; cognition is optional

---

*AUTORESEARCH_UI_V1 · NON_SOVEREIGN · authority=false · HELEN OS — created by JM Tassy*
