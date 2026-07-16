# Goblin Warren: Second Bloom

```
status: PHASE 1 — Level 1 playable · authority=false · canon=false
ledger_effect: none · HOLD_FOR_OPERATOR
isolated product — no dependency on apps/goblin-warren/ (V1 untouched)
```

A cozy living-world game where every small choice changes what goblins
notice, do, remember, and build together. Built from the compost of every
earlier Warren (see `SECOND_BLOOM_LEGACY_DIGEST.md` and
`SECOND_BLOOM_COMPOST_VERDICT_V0.md`).

## Level 1 — The Dying Fire

The Embodied Delegation Ladder in 90 seconds:

1. **KINDLE** — press and hold the ember. The fire wakes. Bram wakes.
2. **DRAG** — pull the twig into the flames. Firelight reveals a wood pile.
3. **The limit** — drag the big wood. It will not move. A soft glow appears.
4. **MARK** — tap the glowing wood. Your mark intensifies… Bram pauses,
   turns his head, walks over, and carries the wood to the fire.
5. **Together** — the fire grows strong; the lantern lights.

The player never reads an explanation of delegation. The world teaches it.

## Run

```bash
bash run_local.sh          # → http://localhost:8321
```

## Test

```bash
node tests/test_level1_invariants.mjs
```

47 checks, including the hard laws: MARK never directly resolves a need;
KINDLE/DRAG never assign Bram a task; trace peak precedes orientation
precedes movement precedes delivery; the failed drag precedes the hint;
pause costs nothing; same seed + same actions = identical world and
telemetry; no randomness, no network, no wall clock, no HELEN paths in src.

## Architecture

```
src/core/         determinism (seeded LCG, fixed-step ticks) · events · state
src/game/         traces · needs (fire barometer) · goblins (deterministic FSM) · persistence
src/content/      strict level schema (unknown fields fail) · L1 data
src/render/       canvas renderer (placeholder art tier — procedural, seeded)
src/ui/           HUD (objective, pause, calm mode, resume banner)
tests/            invariant suite (Node)
```

Input is abstracted: `KINDLE / DRAG / MARK` are events. V0 binds them to
hold / drag / tap — the composted tactile pack (blow, shake, tilt) can rebind
them later without touching game logic.

Telemetry is local game telemetry only — not a HELEN receipt, not a ledger.
Persistence is localStorage only — not canonical replay.

## Not yet (honest)

- Art is procedural placeholder tier (Phase 2 replaces it against the asset
  boards, with `assets/manifest.json` provenance).
- No audio (hooks land in Phase 5).
- Lulu is background-only (active from Level 2).
- No human playtest has occurred; automated tests establish mechanical
  readiness only.
```
