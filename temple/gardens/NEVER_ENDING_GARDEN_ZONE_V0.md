# NEVER_ENDING_GARDEN_ZONE_V0

```
AUTHORITY      = false
CANON          = false
LEDGER_EFFECT  = NONE
STATE_MUTATION = NONE
ROUTE          = temple/gardens (TEMPLE · non-sovereign)
STATUS         = design / sandbox spec
CLAIM_STATUS   = garden_design
VERSION        = V0
PROMOTION      = FORBIDDEN_WITHOUT_PEER_REVIEW_AND_REDUCER
```

> The garden may grow forever. The ledger admits nothing without a human.
> Growth is infinite; admission is bounded. That asymmetry is the safety.

---

## 0. What this is

A **perpetual, bounded, non-sovereign growth zone**. The garden never stops
generating — personas play, claims are made, structures accrete — but nothing it
grows is ever true, admitted, or canon until a human reducer says so. It grows
without rotting because it has an **immune system**: every growth is bound to an
oracle and measured for drift, never trusted on confidence.

This is not a new framework. It is the session's findings wired into one loop:
- the growth engine = bounded autoresearch epochs (existing)
- the immune system = `REFERENCE_DRIFT_WITNESS_V1` (existing, ledger-proven)
- the safety law = `GROWN ⊬ ADMITTED` (the membrane, everywhere)

---

## 1. Why it never ends — and never overflows

```
growth(garden)    = ∞     unbounded generation in the sandbox
admission(canon)  = finite, human-gated
∴ the garden expands forever, but sovereign reality grows only at human speed
```

The danger of an infinite generator is rot: unverified output piling into truth.
The garden defeats rot not by stopping growth but by **never letting growth
self-admit**. Infinity is safe because the gate is finite.

```
NEVER_ENDING   = generation loop has no terminal state
GROWING        = each epoch accretes structure (kept, flagged)
SAFE           = nothing crosses to canon without ALLOW_human
```

---

## 2. The growth loop (the engine)

```
   ┌──────────────────────────────────────────────────────────┐
   │  SEED → GROW → WITNESS → FLAG → SEAL(epoch) → RE-SEED ↺   │
   └──────────────────────────────────────────────────────────┘

   SEED      carry-forward state from prior epoch (no fabrication)
   GROW      personas generate: claims, structures, contests
   WITNESS   each growth bound to its oracle → drift measured (§4)
   FLAG      classify COUPLED / SOFT_DRIFT / HARD_DRIFT (§4)
   SEAL      epoch sealed with a receipt; nothing promoted
   RE-SEED   next epoch opens from sealed state
```

Each epoch is **bounded** (one hypothesis / one growth-step per epoch, halt
before the next opens). The *loop* is unbounded; the *epoch* is finite. This is
the existing PULL-mode tranche discipline applied perpetually.

---

## 3. The gardeners (personas, oracle-bound)

Each TEMPLE persona is a gardener with a declared domain and a bound oracle:

```
🧌 GOBLIN   feral generation     oracle: git / filesystem (did it actually write?)
🛡️ DAN      boundary / structure oracle: ledger hash-chain (does the receipt verify?)
🎭 JESTER   play / recombination oracle: replay (is the state reconstructible?)
🌹 HER      meaning / continuity oracle: memory spine (is continuity real, not invented?)
```

A persona may be feral, strange, generative — but it is **always checked against
its oracle**. "Feral but kind, strange but useful" — and never trusted on its own
word.

---

## 4. The immune system — DRIFT_WITNESS (apply, don't rebuild)

Engine already exists: `tools/witness_projection_probe.py` + the
`oracle_town/skills/reference_drift_witness` skill (ledger runs
`REFERENCE_DRIFT_WITNESS_V1_RUN_*`). The garden *applies* it per gardener.

```
DRIFT_WITNESS(persona) = distance( persona_reported_state , oracle_verified_state )

   pi_struct  binary structural checks (any FAIL → HARD_DRIFT)
   pi_num     value-vs-baseline (divergence beyond tolerance → SOFT_DRIFT)
   _classify  → COUPLED | SOFT_DRIFT | HARD_DRIFT

   COUPLED      may speak · admissible to validation
   SOFT_DRIFT   VISIBLE · de-weighted · held for review (not silenced)
   HARD_DRIFT   quarantined · VISIBLE + NON-ADMISSIBLE · kept for inspection
```

The witness **flags divergence; it never judges truth** (`Π(x) ≠ Truth`). Drift
is data, not failure. A drifted gardener is marked, not muted — its output stays
inspectable. This is what lets the garden grow feral without going false.

---

## 5. Contest is kept, never suppressed

When gardeners disagree, the disagreement is preserved as a first-class artifact:

```
CONTEST(growth) ∈ garden_record    always visible
I(contest) > 0                      disagreement carries information
```

And the session's live lesson: when uncoordinated gardeners' *reports* diverge,
the gap itself localizes a hidden fact (an active external writer, a stale read,
a race). **Inter-gardener divergence is a free, decentralized drift sensor** —
measured against the oracle, never resolved by vote.

---

## 6. The fail-closed laws (so infinite growth stays safe)

```
GROWN        ⊬ ADMITTED        generation ≠ truth
dream        ⊬ claim           play ≠ assertion
symbol       ⊬ canon           beauty ≠ evidence
witness flags ⊬ verdict         divergence ≠ judgment (Π ≠ Truth)
NO_RECEIPT   → NO_VOICE         unreceipted growth cannot speak in the surface
NO_ALLOW     → NO_ADMIT         only the human reducer crosses growth into canon
garden       ↛ sovereign spine  nothing here mutates kernel / ledger / schema
```

The garden cannot touch the firewall. It writes only to `temple/gardens/**` and
`sandbox/**`. Its richest output is still `authority = NONE`.

---

## 7. What's reused vs what's new

```
REUSED (zero build):
   · bounded autoresearch epoch loop (PULL-mode discipline)
   · witness_projection_probe.py + reference_drift_witness skill + ledger runs
   · WITNESS_REPORT_*.json report shape
   · the membrane: GROWN ⊬ ADMITTED · human ALLOW = sole canon gate

NEW (thin wiring):
   · a per-gardener oracle map (§3)
   · the perpetual SEED→GROW→WITNESS→FLAG→SEAL→RE-SEED loop framing (§2)
   · the admissibility gate keyed on drift class (§4)
```

---

## 8. Minimal runnable next step (not yet built)

```
sandbox/autoresearch/garden_zone/garden_persona_witness.py   (authority=NONE)
   - map each persona → oracle
   - wrap witness_projection_probe per persona
   - gate admissibility on _classify verdict
   - emit one WITNESS_REPORT per gardener per epoch
   - loop bounded epochs; seal each; never promote
```

No commit, no ledger, no push. Operator authorizes the scaffold separately.

---

## 9. Seal

```
🌱 the garden never stops growing
👁️ every gardener bound to an oracle · drift flagged, never silenced
🧾 GROWN ⊬ ADMITTED · contest kept · human ALLOW = the only gate to canon
♾️ growth = ∞ · admission = finite · the asymmetry is the safety
authority = NONE · canon = false · ledger_effect = NONE
🏁
```
