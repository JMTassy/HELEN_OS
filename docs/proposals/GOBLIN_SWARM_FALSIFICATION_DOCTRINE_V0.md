# GOBLIN SWARM FALSIFICATION DOCTRINE V0 — Role-Separated Research Swarm

```
type:           PROPOSAL
authority:      false
canon:          false
ledger_effect:  none
claim_status:   NO_CLAIM
parents:        AUTORESEARCH doctrine · governed-self-improvement ·
                HELEN_SIGIL_REGISTRY_MERGE_V0.md
final:          HOLD_FOR_OPERATOR
date:           2026-08-04
```

HELEN OS — created by JM Tassy.

---

## 1. Theorem (multiplicative)

```
frontier_gain = 🌀diversity × 🕊️independence × 📏fixed_evaluation
```

Any factor at zero zeroes the product. 10 copies voting: independence→0,
gain→0 — correlated error × 10, regardless of model count. Same law as
Trust = Resolved × Type × Linkage × Cross-Seat: governance is
multiplicative, more agents never compensate a dead factor.

```
10 × copies voting     = correlated error × 10
10 × separated roles   = broader search + stronger falsification
```

## 2. Role split (10 goblins, canonical)

| n | Role | Function | Sigils |
|---|------|----------|--------|
| 2 | BRAM | smallest repairs | 🌱⚗️ |
| 2 | HAL | falsifiers | 🪨⚖️⚔️ |
| 1 | CHRONOS | repetition / lineage detection | ⏱️🌀 |
| 1 | PIP | missing-evidence hunter | 👁️🧾 |
| 1 | ASH | risk / blast radius | 🧿⚠️ |
| 1 | MOSS | prior-results comparison | 📚🕸️ |
| 1 | MAYOR-sim | readiness (SIM ONLY — not sovereign MAYOR) | ⚖️ |
| 1 | SCOUT | new hypotheses | 🌱🌓 |

HER generates (🌹🌀: vision, pattern synthesis, symbolic compression,
experiment proposals). HAL falsifies (🪨⚖️). Neither may alter truth
conditions.

## 3. Hard limits

```
same baseline · same evaluator · same dataset · same ENVIRONMENT_HASH
one mutation per branch
no majority vote
no self-admission           🏛️ = 0 inside the swarm, always
no evaluator mutation       HER limit — frozen judge
no silent protocol rewrite
no self-reported certainty as evidence   (🫀 is signal, never 🧾)
KEEP ≠ SHIP ≠ CANON
```

## 4. Judge validation precondition (Goodhart guard)

A frozen judge is necessary but not sufficient. Standing lesson: regex/
vocabulary scorers produced false negatives on correct answers — the metric
diverged from fitness. Therefore, BEFORE any swarm run:

```
1. run judge on ≥10 known-good + ≥10 known-bad raw outputs
2. operator reads RAW answers, not scores
3. judge ships with its own 🧾 validation receipt
no validated judge → no run (fail closed)
```

A swarm optimizing against an unvalidated judge farms Goodhart, not truth.

## 5. Epoch loop (per-epoch receipted, decision external)

```
🎯 objective (frozen)
→ 10×🌱 hypotheses
→ ⚖️ deduplicate (vs seen, not vs kept)
→ ⚗️ parallel branches (one mutation each, worktree-isolated)
→ 📏 same validated judge
→ ⚔️ falsify (HAL roles, prompted to refute)
→ ✅KEEP / 🔙ROLLBACK — decided OUTSIDE the proposing branch,
   receipted per epoch, per anti-RALPH law: the loop never
   self-decides KEEP silently, never skips an epoch receipt
→ 🧠 merge search memory (lineage via CHRONOS)
→ 🌀 next epoch
🏁 closure: SHIP-candidate list → operator → reducer. Never direct.
```

Epoch verdicts: `SUCCESS | FAILURE | INVALID_EXPERIMENT` — the third is
mandatory (a broken harness is not a confirmation; anchor-cut discipline).
Record observed information gain per epoch; a dry epoch is data.

## 6. Environment stability (AR-11)

```
ENVIRONMENT_HASH = hash(model version, params, dataset, judge, harness)
```

Pinned before epoch 1; any change → all cross-epoch comparisons INVALID
until replayed under the new hash. Mutation dependency graph maintained so
a rollback (🔙) knows its blast radius (ASH).

## 7. MVP (first run, bounded)

```
1 task            🎯 JSON-schema compliance
1 model           GOBLIN_GEMMA
1 mutation/branch  one prompt or parser field
1 evaluator       fixed schema judge — validated per §4 first
1 ENVIRONMENT_HASH
5 competing hypotheses × 2 replicas · 10 goblins · 3 epochs max
👁️ freeze baseline · ⚔️ preserve raw failures · 🧠 record all
```

## 8. Seal

```
🌀10 ⚖️1 🏛️0 🧠↑ 🏁
```

Ten explorers, one judge, zero authority, memory grows. The swarm may
discover; it may not admit. Everything it keeps is a REVIEWED_CANDIDATE
awaiting the reducer — never a verdict.
