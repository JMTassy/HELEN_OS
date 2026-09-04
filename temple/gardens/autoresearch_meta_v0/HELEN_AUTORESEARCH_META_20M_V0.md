# 🔬 HELEN_AUTORESEARCH_META_20M_V0 — research on the research loop

```
AUTHORITY=false · CANON=false · LEDGER_EFFECT=none · LOCAL_FIRST · FABLE_CALLS=0
Cognition on the process, not the domain. No promotion. Candidate spec only.
Evidence: meta_falsifier.py (deterministic, file-backed) · META_FALSIFIER_RESULT.json
```

## CURRENT_LOOP (reconstructed from real artifacts, not prose)

```
CHAOS(run_chaos_garden.py) → GATE(run_chiddush_gate.py) → GENESIS(run_genesis_loop.py)
  entry           : CHAOS emits objects/*.json (self-tagged WHY_NOT_JUST_RENAMING)
  falsifier gen    : GATE = HAL adversarial counterfeit + discriminator per object
  verdict          : SURVIVES | RENAMING_ONLY→COMPOST | EVIDENCE_NEEDED
  seed handoff     : GATE writes CHIDDUSH_S0.json = survivors[:3] IF survives≥3
                      ELSE sorted(results,-fitness)[:3]           ← LAUNDERING BRANCH
  next iteration   : GENESIS.load_seeds() returns CHIDDUSH_S0.json IF it exists
                      (BEFORE the SEEDS_NOT_READY guard)          ← BYPASS BRANCH
  stop rule        : GENESIS dryness ρ<ε for DRY_MAX epochs (present)
  falsifier memory : UNKNOWN → none (falsifiers not carried across the boundary)
  provenance/root  : UNKNOWN → no root-census before "seed" promotion
  epoch admission  : UNKNOWN → epochs run unconditionally (no pre-exec gate)
```

## DISCOVERED_FAILURE_MODES (one reproduced with hard evidence; others held)

- **M3 counterexample-amnesia ∧ M7 pass-leakage — REPRODUCED.** With `gate.survives=0`,
  `CHIDDUSH_S0.json` still contains **3 `EVIDENCE_NEEDED` seeds**; `load_seeds()` returns
  them, so GENESIS seeds on non-survivors and the "0 CHIDDUSH survived" falsifier is lost.
  `CURRENT_LOOP_DETECTS = NO`. Witness: `meta_falsifier.py → DEFECT_REPRODUCED=True`.
- M1 confirmation-loop, M6 semantic-drift, M8 unbounded-search, M9 false-recursion — **UNKNOWN/HELD** (not reproduced this run; do not count as killed).

## MINIMIZED_COUNTEREXAMPLE

```
gate.survives = 0  ∧  |CHIDDUSH_S0| = 3  ∧  ∀s∈S0: verdict(s) ≠ SURVIVES
⇒ GENESIS seeds on 3 non-survivors  ⇒  EVIDENCE_NEEDED laundered into S₀
```
Smallest trigger: `survives < K` with `results` non-empty. The `else sorted()[:3]` branch is the defect.

## PROPOSED_LOOP_DELTA (minimal, witnessed)

```
REPAIR¹  GATE: CHIDDUSH_S0 := survivors ONLY.  If |survivors|<K → write S₀=[] .
         GENESIS.load_seeds: empty/absent survivor-S₀ ⇒ SEEDS_NOT_READY ⇒ STOP.
ATTACK   REPAIR¹ drops the 3 EVIDENCE_NEEDED with no memory ⇒ M10 amnesia (compression⇒amnesia).
REPAIR²  Persist FALSIFIER_MEMORY.json: the "0 CHIDDUSH" open obligation + the
         EVIDENCE_NEEDED items as HOLD, carried until an explicit resolution receipt.
```
Witness: `meta_falsifier.py` — REPAIR_FIXES_DEFECT=True, REPAIR_INTRODUCES_AMNESIA=True,
AMNESIA_AFTER_REPAIR²=False, CHAIN_VALID=True.

## OLD_LOOP → CANDIDATE_NEW_LOOP (AUTORESEARCH_V1.1)

```
OLD:  CHAOS → GATE → (launder) → GENESIS(seed on anything)
NEW:  RECOVER → DIFF → ROOTS → ATTACK → OBSERVE → MINIMIZE → REPAIR → REPROVE → NOVELTY → STOP? → RECEIPT
      + EPOCH_ADMISSION gate     : reject epoch unless IG>0 ∧ F≠∅ ∧ O≠∅ ∧ D⁺≠D⁻
      + M_F falsifier memory      : Falsifier_t ∈ M_{t+n} until resolution receipt
      + Q_prov root-census        : raw→roots→independence→contradiction→weight  (N_repr↑ ⇏ N_epi↑)
      + Γ_stop dryness gate        : max_x IG(x)<τ for m cycles ⇒ MARGINAL_INFORMATION_DRYNESS (never THEORY_PROVEN)
```

## WHY_NEW_LOOP_IS_STRONGER

- **No decision delta, no epoch.** `D⁺=D⁻ ⇒ IG≈0 ⇒ reject before execution` — kills novelty-theater at the gate, not after.
- **Null result allowed; non-discriminating design is not.** A survivors-only S₀ that STOPs is a *valid* null; laundering is not.
- **Compression ⇏ amnesia.** `M_F` makes the "0 survived" falsifier a blocking obligation, not a rounding error.
- **`N_repr↑ ⇏ N_epi↑`** moves from external note into loop core via `Q_prov`.

## WHAT_NEW_LOOP_STILL_CANNOT_PROVE

- Garden→Kernel **non-amplification** (`∀p: GardenEntry⇝GovernedMutation ⇒ LicensedGate∈p`) — separate bead (mutation falsifiers M₁…M₆).
- That `IG = Dist(D⁺,D⁻)` is a **calibrated** information gain — it is an ordinal/inspectable heuristic only, not Bayesian.
- That a gate-`SURVIVES` object is **true** — surviving-the-counterfeit ≠ true (`Novelty≠Evidence` still holds).

## RECURSION_TEST_RESULT (depth 2, cap respected)

REPAIR¹ was attacked → produced a *new* defect (amnesia) the old loop would miss → REPAIR² fixed it.
Depth-2 attack on REPAIR²: **NEXT_DEEPEST_ATTACK** below. Stopped at depth 2 per cap.

## PERMANENCE_TEST → CANDIDATE (no auto-canonization)

Repairs a demonstrated failure ✓ · no authority widening ✓ · minimal new concept (`M_F`, epoch gate) ✓ ·
explicit falsifier (`meta_falsifier.py`) ✓ · preserves UNKNOWN/HOLD ✓ · preserves provenance independence (`Q_prov`) ✓ ·
prevents pass→completion (survivors-only + gate) ✓ · deterministic stop (`Γ_stop`) ✓ · versionable ✓ · replayable from receipt ✓.
→ **PERMANENCE = CANDIDATE**, not admitted.

## SEMANTIC_VERSION_CANDIDATE

`AUTORESEARCH_V1.1` (additive: EPOCH_ADMISSION gate + M_F + Q_prov + Γ_stop; no removal, no authority change).

## NEXT_DEEPEST_ATTACK

The `D⁺≠D⁻` gate uses *inequality of stated decisions*. Attack **M6-at-decision-level**: an epoch declares
cosmetically-distinct D⁺/D⁻ that are **operationally identical** (same downstream action). The gate passes;
IG is really ≈0. Repair would require a *decision-equivalence* check (canonicalize D⁺,D⁻ to their effect),
not string inequality. Held for the next meta-bead.

```
STATUS: CANDIDATE_ONLY · authority=false · not admitted · not canon · ΔA=0 · NO_CLAIM
```
