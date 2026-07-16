# LEVEL 2 — THE QUIET SIGNAL (spec V0, banked for Phase 3)

```
authority: false · canon: false · ledger_effect: none · HOLD_FOR_OPERATOR
source: operator-supplied design (B-then-C session) + vision lock §5
status: SPEC ONLY — not implemented; Gate: operator GO for Phase 3
```

## One concept only

**Different goblins notice and prioritize different signals.**
L1 taught "I can make a goblin act." L2 teaches "WHICH goblin acts depends on
what I mark." Specialization felt, not told.

## Structure

- Zone: garden (fire from L1 visible, stable, warm — continuity).
- Active: Bram + Lulu. Verbs: MARK + INTERVENE (new — direct fix on a need),
  no other additions.
- Two simultaneous needs:
  | Need | Trace type | Who responds | Board need-states |
  |---|---|---|---|
  | Cracked Root | WARNING (orange) | Bram (WARNING affinity 1.0 / Lulu 0.4) | cracked → marked → bram-on-way → repairing → repaired |
  | Dry Moss Patch | RESOURCE (golden) | Lulu (novelty seeker, low threshold) | dry → noticed → investigating → gathered |
- Action budget: 3 (first appearance of limited attention — kept gentle,
  no counter pressure UI; tokens per the board's action-token design).
- Deterministic: same marks → same reactions, always (players must be able
  to LEARN the pattern; the profiles in `src/game/goblins.js` already encode
  the asymmetry — Bram actThreshold 100/WARNING-affine, Lulu threshold 30/
  novelty-affine).

## Designed learning moments

1. Mark the root → Bram full chain; Lulu glances (brief orient, returns).
2. Mark the moss → Lulu investigates; Bram shows no interest.
3. Emergent: "same verb, different responders."
4. Optional payoff: both needs helped → Bram and Lulu share a brief
   proximity moment (wave/laugh, page-3 animations) — a seed of coordination,
   not a mechanic.

## Success criteria (player's own words)

"Bram cares about things that need fixing." · "Lulu chases interesting
things." · "Marking something doesn't make everyone react the same way."

## Engine deltas required (estimate, Phase 3)

- INTERVENE verb (direct resolution on a need object) + isolation invariants
  mirroring L1's (INTERVENE never assigns any goblin a task).
- Needs as data-driven state machines (the board's need-state rows).
- Lulu FSM activation (profile exists; needs glance-and-dismiss behavior for
  low-affinity peaks — a *partial* orient that visibly aborts).
- Action budget in world state + gentle token UI.
- L2 invariant suite: affinity asymmetry (root-mark never moves Lulu to
  repair; moss-mark never moves Bram), budget enforcement, determinism.

## Asset boards adopted (operator-supplied, 2026-07-16)

Two sprite-sheet boards + page 3 now define Phase 2 direction: character
keyframes (Bram repair cycle = idle/notice/turn/walk/repair/done — matches
the shipped causal chain 1:1), FX set (tap pulse, trace pulse, notice spark,
orient arrow, repair sparks, memory ripple, bloom, fog swirl), need-state
strips, larder (12 items incl. moss tea, glow berries, sprout soup), bestiary
(Popfung, Glow Mite, Rootling, Berrybug, Puffwisp, Shellbud), UI tokens
(INTERVENE/MARK/GIVE/LISTEN/PLACE), color palette. Status: AI-generated
concept art, reference only — production assets require `assets/manifest.json`
entries with provenance. Concept art ≠ playable asset.
