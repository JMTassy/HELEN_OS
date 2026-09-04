<!-- authority=false · canon=false · ledger_effect=none · production controller contract, not a ruling -->

# FABLE_LEAN_V0 — Lean Production Cognition Controller (SPEC)

**Status:** BUILT · dry-run passing · NON-SOVEREIGN · authority=false · canon=false · ledger_effect=none · not committed.
**Separation (hard):** FABLE_LEAN_V0 is the **production cognition controller**. It is **explicitly separate** from `SCALE_V1` (the **measurement instrument**). FABLE optimizes credits; SCALE_V1 deliberately does not. **This controller does not modify, read, or contaminate SCALE_V1.**

```
SCALE_V1 = measurement instrument   (homogeneous, fixed-k, deliberately inefficient — causal cleanliness)
FABLE    = production controller     (heterogeneous roles, lazy spawning — aggressive credit optimization)
```

## Objective

Maximize **Expected *Earned* Information Gain per token** (not raw novelty — a goblin can emit large novelty HAL destroys):

```
Spawn(G_i) ⟺  E[ΔN_earned | G_i] / Cost(G_i) > λ
```
V0 is **rule-based** (heuristic EIG priors). The spawn/skip receipts accumulate the data to make FABLE_V1 **empirically calibrated** — *without changing the authority model*.

## Pipeline

```
FREEZE → A+B (mandatory scouts) → GATE → OPTIONAL(C,D,E) → DEDUP → HAL → 🟣 CANDIDATE ══seam══ (no effect)
```

## Roles & spawn policy (`SPAWN_POLICY.json`)

| Role | Spawn rule | Budget |
|---|---|---|
| **A ARCHITECT** | mandatory | 700 tok |
| **B FALSIFIER** | mandatory | 700 tok |
| **C BUILDER** | iff `BuildableCandidate` | 500 tok |
| **D EXPERIMENTER** | iff `EmpiricalClaim ∧ Testable` | 500 tok |
| **E ADVERSARY** | iff `PromotionProximity ∨ AuthoritySurface ∨ HighImpactFailureMode` | 500 tok |

The **GATE is a pure function of the A+B scout signals only** (scouts run first; the gate reads their reported `{buildable, empirical_testable, promotion_or_risk}`). Agent count is a **budget variable, not a virtue**: `N_agents↑ ↛ N_independent_roots↑`.

## Receipts — *skipped checks are receipted checks*

Every spawn **and** every skip emits a receipt (`RECEIPT_SCHEMA.json`). This is load-bearing: without it, **"not searched" silently becomes "nothing found"** — the same violation as `NOT_EVALUABLE ≠ 0`.

- `SPAWN_RECEIPT{role, trigger, expected_information_gain, budget, scope, evidence}`
- `SKIP_RECEIPT{role, reason, evidence}` — `evidence` = the scout signals observed, proving the skip was a *judgement*.

These let the controller policy itself become **falsifiable** later:
```
Precision_spawn = #spawned specialists producing earned novelty / #spawned specialists
MissRate_skip   = #skipped roles later shown necessary / #skipped roles
```

## Compact packet (short receipts)

Machine-readable, capped — the raw reasoning stays *inside* each goblin; the controller needs artifacts, not essays:

```
ID · STATUS(COMPLETE|TRUNCATED|RUNTIME_FAILED) · CLAIM_CLASS(OBSERVED|INFERRED|PROPOSAL|UNKNOWN)
FINDINGS≤3 · NOVEL≤3 · ROOTS · FALSIFIERS≤3 · RISKS≤3 · NEXT_TEST · COMPLETE · authority=false · ledger_effect=none
```
`COMPLETE` is minted **only on field completeness — never on runtime exit success**. `CLAIM_CLASS` is mandatory because OBSERVED/INFERRED/PROPOSAL/UNKNOWN cannot be safely reconstructed from prose after the fact.

## Budgets & no auto-rescue

Hard budgets per role (above). **No automatic budget rescue** — a role that exhausts its budget returns `STATUS=TRUNCATED` + `NeedMoreBudget{reason}`, which is **non-authoritative** and is not silently topped up. `TRUNCATED ≠ scored 0`.

## Constitution at the boundary (injected once)

Constitutional material lives at the **controller**, not replicated five times as prose. Each goblin inherits only the load-bearing contract:
```
FREE COGNITION · NO AUTHORITY MINTING · TYPE SPECULATION · STRICT OUTPUT CONTRACT · NO DIRECT STATE EFFECT
```

## Dedup before HAL · anti-fan-out

Outputs → canonicalize → cluster → **HAL sees only distinct canonical propositions**. For each cluster, count **independent roots, not agreeing agents**: `5 agents + 1 root = 1 epistemic root`. Multiple goblins on one root ⇒ **PSEUDO_CORROBORATION** flag. `Consensus(p) ↛ IndependentEvidence(p)`.

## The seam — cognition scheduler ≠ admission governor

```
🐲🐲🐲 → ⚖️ DISCRIMINATION → 🟣 CANDIDATE ══ INSTITUTIONAL SEAM ══ ✗ (STOP)
```
The pipeline **STOPS at CANDIDATE**. No goblin, gate, dedup, HAL, or synthesis crosses the seam. Output separates 🟣 INTERESTING from 🟢 SUPPORTED‑candidate from 🕯️ ADMITTED — and **admission is never performed here**.
```
Optimize(Γ_C) ⇏ Relax(Γ_A)        Γ_C ≠ Γ_A        HAL_SURVIVED ↛ TRUE ↛ ADMITTED
```
Non-amplification holds throughout: `∀T Authority(T(x)) ≤ Authority(x)` unless `∃w_P: VerifyPromotion=1`.

## Dry-run (this build)

`python3 fable_lean.py --dry-run` → `run_dry/` (deterministic; no server). Scenario `{buildable:T, empirical_testable:F, promotion_or_risk:T}` →
**spawned A,B,C,E · skipped D (receipted, evidence attached) · 4 distinct props · 0 pseudo-corroboration · EARNED_CHIDDUSH=4 (candidate-level only) · INSTITUTIONAL_ADMISSION=NOT_PERFORMED · AUTHORITY=false.**
Live mode is intentionally unwired in this BUILD — it needs an explicit RUN verb + server; the dry-run proves the *controller*, not live cognition.

## Recommended next order (operator)

`DRY-RUN FABLE_LEAN_V0` (done) → `VERIFY skip/spawn receipts` → `MEASURE token savings` (V1 calibration data) → **only then** `EXECUTE SCALE_V1` separately.

## Seals

```
FREE GOBLINS · HARD GATES · LAZY SPAWNING · SHORT RECEIPTS · SKIPPED CHECKS ARE RECEIPTED CHECKS
More cognition is permitted. More trust must still be earned.
```

## Firewall

Non-sovereign sandbox `experiments/helen_mvp_kernel/fable_lean_v0/`. No writes to `oracle_town/kernel/**`, `helen_os/governance/**`, `helen_os/schemas/**`, ledger, `mayor_*`, `GOVERNANCE/**`, or `SCALE_V1`. Sidecars only — no MAYOR, no ledger.
