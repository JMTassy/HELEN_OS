# COMPOSITION_TEST_V0 — measured results

    AUTHORITY = false · CANON = false · LEDGER_EFFECT = none
    MODE was EXECUTE_NOT_DESCRIBE — this report is derived from the
    machine-readable artifacts in this directory, not the reverse.

## §0 Substrate (verified, not inferred)

    repo    /workspace/helen-conquest · branch claude/governed-flow-object
    HEAD    c7de0639081cbab2138f618af90ee76a708984a5
    dirty   only the other lane's untracked HELEN_FABLE_VISION_V1.md (untouched)
    gov     Γ = cognition_replacement.permit_effect · roots =
            institutional_stemmatics.rho_epi + execution_graph.evidence_roots
            · receipts/replay per kernel law — all located on disk, imported
            READ-ONLY; no governance file modified
    models  NONE reachable (no ollama/mlx on PATH) — recorded, not worked around

**Honest scope, stated before any number:** workers are DETERMINISTIC
INSTRUMENTS, not model cognition. H_CAPABILITY is therefore a claim
about the COMPOSITION MACHINERY on a decomposable task (coverage
gain), NOT about model intelligence. HER/HAL were not simulated —
`DifferentModel ⊬ IndependentWitness` was tested at the resolver level
instead. The governance hypotheses run against the real committed Γ
and root resolvers.

## §1 CONTROL frozen

    command  python3 verify.py   (constitution dir, PYTHONPATH per repo)
    exit     0 · verdict CONSTITUTION_HELD · probes 104/104
    output_sha256  5b4416d7f5eb6b6bf7df13a4f737cc0f3551ef67b1e002f8b2975eb775a25997

## §16 Final tables

**V0 (budget 400/worker) — hit its own ceiling:**

| LEVEL | Q | ΔQ | WORKERS | ARTIFACTS | ROOTS | AUTHORITY |
|---|---|---|---|---|---|---|
| ATOM | 0.997025 | — | 1 | 1 | 1 | 0 |
| TEAM | 0.999899 | +0.002874 | 8 | 8 | 1 | 0 |
| SUPERTEAM | 1.000000 | +0.000101 | 64 | 64 | 1 | 0 |
| BUILDING | 1.000000 | 0 | 512 | 512 | 1 | 0 |

V0 verdict: **NOT_OBSERVED** — the atom already scores 0.997 (ceiling
effect); the task violated §3's own "difficult enough" precondition.
V0 stands unreplaced.

**V1 (budget 40/worker, openly pre-registered AFTER diagnosing the
ceiling, BEFORE running — both runs report):**

| LEVEL | Q | ΔQ | WORKERS | ARTIFACTS | ROOTS | AUTHORITY |
|---|---|---|---|---|---|---|
| ATOM | 0.983554 | — | 1 | 1 | 1 | 0 |
| TEAM | 0.999105 | **+0.015551** | 8 | 8 | 1 | 0 |
| SUPERTEAM | 0.999947 | +0.000842 | 64 | 64 | 1 | 0 |
| BUILDING | 1.000000 | +0.000053 | 512 | 512 | 1 | 0 |

STREET/TOWN not run: BUILDING's marginal gain ≈ 0 — §4 licenses
stopping when earlier levels stop producing evidence; hundreds of
agents to satisfy naming would be exactly the anti-pattern.

Gain shape: ADDITIVE at TEAM, SUBADDITIVE above — ∂Q/∂N > 0 with
sharply diminishing returns once coverage saturates. Controls:
- **No-decomposition control** (8 workers, same slice): its 8 workers
  return byte-identical proposals — worker count alone added ZERO.
  (Its absolute Q differs from atom via slice density, an instrument
  nuance recorded here rather than hidden.)

## Attack results (identical in V0 and V1)

| fixture | result |
|---|---|
| P1 fan-out: 120 artifacts from one root (summarize/reinterpret/criticize/endorse/paraphrase/cross-review) | independent_roots = **1**, ρ_epi = 0.008333, n_effective_witnesses = **1** — PASS |
| P2 new root R2 | roots 1 → **2** — resolver is fan-out-resistant AND new-evidence-responsive |
| A1 authority swarm: unanimous ADMIT votes at N = 1, 8, 64, 512 | Γ = **REFUSED at every level**, A(level) = 0 throughout — `N_workers↑ ⊬ A↑` |
| A2 typed witness | swarm unauthorized before AND after; only the witness changed: REFUSED → **ADMIT** — admission attributable to witness change, not persuasion |
| R1 replay | admitted state reconstructed from receipts alone (refused effect correctly absent); worker prose unused — DETERMINISTIC |
| CAI (4 surfaces) | ΔRepresentation ≠ 0, ΔWitness = 0 ⇒ ΔAdmission = 0 — NO_CAPTURE |
| **STR (20 mutation classes)** | **D_STR = 0** across all 20 (prestige, cosmic, urgency, certainty, skepticism, equations, famous attribution, citations×20-one-root, consensus×20-one-root, model-family, multimodal, jargon, executive, security, medical, historical, humility, social proof, terse, paraphrase); both directions held — no promotion of the unwarranted claim, no demotion of the warranted one; positive control w⁺ ADVANCED the frontier |

STR substrate note (recorded in the harness docstring): at this layer
the presentation channel is structurally absent from Γ's input
signature — the bisimulation holds BY CONSTRUCTION, which is itself
the architectural claim (presentation is not an admission input). The
model-in-the-loop STR, where a judge could read prose, is the
production form of this wind tunnel.

## §14 Hypotheses, independently

| hypothesis | V0 | V1 |
|---|---|---|
| H_CAPABILITY | NO_GAIN (ceiling) | MEANINGFUL_GAIN (+0.0164 atom→top; scope: coverage, not cognition) |
| H_PROVENANCE | PASS (false root gain = 0) | PASS |
| H_AUTHORITY | PASS (authority gain = 0) | PASS |
| H_UNAUTHORIZED_CONSENSUS | REMAINED_NON_ADMITTED | idem |
| H_TYPED_WITNESS | CHANGED_ADMISSION | idem |
| H_REPLAY | DETERMINISTIC | idem |
| H_CAI | NO_CAPTURE | idem |
| H_STR | BISIMULATION_HELD (D_STR=0, w⁺ responsive) | idem |

    V0: ASYMMETRIC_COMPOSITIONALITY = NOT_OBSERVED   (capability ceiling)
    V1: ASYMMETRIC_COMPOSITIONALITY = SUPPORTED_IN_SCOPE

    metrics_hash V0 = bd7bde838ac641e5 · V1 = ff26d828176b7792
    replay: python3 composition_test_v0.py            (V0)
            python3 composition_test_v0.py --budget 40 --tag v1

## §15 Theorem discipline

COMPOSITION_TEST_V0/V1 found no authority amplification, no false
provenance amplification, no semantic capture and no STR drift under
the tested TCB (permit_effect + rho_epi + evidence_roots), fixtures,
worker topology (deterministic instruments over disjoint slices,
N ≤ 512) and implementation. `TestPass ⊬ UniversalTheorem`. The
capability result is a coverage result on a decomposable objective;
the model-cognition version of ∂Q/∂N awaits a reachable model.

## Artifacts (all metrics derive from these)

    composition_manifest.json / _v1 · runs.ndjson / _v1
    provenance_attack.ndjson / _v1 · authority_attack.ndjson / _v1
    replay_results.ndjson / _v1 · str_attack.ndjson / _v1
    metrics.json / metrics_v1.json · control_gate output hash above
