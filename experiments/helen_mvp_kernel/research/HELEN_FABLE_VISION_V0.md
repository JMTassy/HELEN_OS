# HELEN_FABLE — Vision as a governed execution graph

    STATUS = CANDIDATE_DOCTRINE
    AUTHORITY = false · CANON = false · LEDGER_EFFECT = none
    SEAT = HELEN_FABLE (narrative/vision) — proposes, never admits
    DATE = 2026-08-15

FABLE's job is to say where this goes next in a way the kernel can
check. So this vision is not a manifesto; it is a graph, and it was
run through `execution_graph.dependency_audit` before being written —
the vision eats the law it proposes to extend.

## The frame (within Anthropic's rules)

Every step below obeys the constitution already sealed:

- **The worker never promotes itself.** Generation ≠ verification ≠
  admission ≠ persistence ≠ truth. Only witnessed admission raises
  reality or authority; FABLE included.
- **No fabricated evidence, no impersonation, no covertly harmful
  capability.** Refusals stay in the data path; receipts are
  re-derivable; instruments absent → HOLD, never a fabricated metric.
- **Probabilistic cognition, deterministic authority.** The model may
  classify and draft; a deterministic gate decides what ships.
- **Vision is a Temple artifact.** `TempleArtifact ⊬ Admission`. This
  document mints nothing.

## What the audit found (receipt, not assertion)

Running the next-steps roadmap through `dependency_audit`:

    declared_edges          18
    real_dependencies       14
    false_edges             4   (deleted from the critical path)
    parallel_width_at_start  9   ← nine steps depend on nothing pending

Nine of the eighteen steps are **startable now** — they consume no
unfinished upstream artifact:

    A8_observability_backup   A9_config_plugins   A13_tma_escrow_dr
    OB_instruments            SK_archaeologist_live_run
    XL_local_lane_push        K_effect_ordering
    K_capability_attenuation  UZ_J8

The parallelism is not in spawning agents; it is in the nine arrows
that were never dependencies. `TASK → REAL DEPENDENCIES → GRAPH →
CONTRACTS → AUTHORITY GATES → AGENT COUNT` — the count comes last, and
here it is small.

*Honest note:* the audit also caught a contradiction in my own model —
`A9_config_plugins → A10_signed_releases` was declared both consuming
and non-consuming. The consuming reading is correct (what gets signed
includes the config surface), so the non-consuming declaration was my
error, surfaced by the falsifier rather than hidden. That is the
mechanism working on the vision, exactly as intended.

## The three real chains (what must be sequential)

Only three sequences carry true data dependencies; everything else
fans:

1. **Enterprise spine (Phase A finish):**
   `A9 config → A10 signed releases → A11 deploy automation →
   A12 BYOC/sovereign`. A8 (observability/backup) and A13
   (TMA/escrow/DR) fan in independently. All six meet at one join:
   **CISO_APPROVAL** — the software a security officer can approve.
   The roadmap gate already in `vnext_architecture.py` says
   autonomous-worker expansion is item 14 of 14; more agents come
   *after* this join, never before.

2. **OBLITERATUS spine:**
   `instruments → baseline → surgery loop → PASS`. This chain does
   NOT depend on the enterprise spine (the audit deleted that edge).
   It is blocked only on three operator-supplied instruments: a real
   842-corpus, a callable model-under-test, a graded evaluator. The
   moment they land, the skill's five scripts run the real baseline
   instead of the honest all-error placeholder.

3. **Memory spine (skills → training):**
   `archaeologist live run → decision_gym`. The archaeologist is
   built; its first live firing (a real "run J3 on <target>" through
   your authenticated connectors) is the gate for decision_gym, which
   turns earned history into governed episodes — never RawArchive →
   Train.

## The FABLE decomposition of "next steps"

Cast as the runtime the operator drew — INTENT → DECOMPOSER → FAN of
worker∥verifier pairs → JOIN → SYNTHESIZER → AUDITOR → ADMISSION →
RECEIPT → LEDGER → REPLAY — the next steps are:

| lane | worker | its verifier (separate seat) | promotes via |
|---|---|---|---|
| Enterprise | build A8/A11/A13 runtimes | adversarial test + gate probe | CISO_APPROVAL join |
| OBLITERATUS | run the frozen audit | `verify_receipt.py` re-derivation | PASS \| HOLD \| REVERT |
| Memory | archaeologist live corpus run | `claim_validator` / `episode_validator` | decision_gym intake |
| Cross-lane | fetch + re-run local lane's tests | differential fixture (two impls, same input) | CROSS_LANE_VERIFIED |
| Kernel | effect-ordering, capability attenuation | new gate probes | verify.py |

Each worker is instantiated as wide as its evidence roots justify —
and **not one wider**: `100 agents ⊬ 100 independent evidence roots`.
The Memory lane in particular runs at N matched to independent
provenance roots, never to the artifact count.

## The one-line vision

> **From one prompt to an arbitrarily wide *governed* execution
> graph** — where breadth is bought by deleting false edges, authority
> is a deterministic gate no worker can mint, and every promotion
> leaves a re-derivable receipt in the ledger.

The number 100 is secondary. The multiplier is
`independent executable work / false dependencies`, and the discipline
is that the count is chosen last, after the shape and the gates.

## Immediate move (FABLE's recommendation, operator decides)

Of the nine startable steps, the highest-leverage single move that
needs **no** operator instrument is **Phase A item 8
(observability/backup)** — it is startable now, it advances the
enterprise spine toward the CISO join, and its verifier (a restore
that proves a backup was real) is itself a clean instance of
`PERSISTENCE ≠ TRUTH`. The three instrument-blocked spines (OBLITERATUS
corpus, archaeologist connectors, local-lane push) stay HOLD until the
operator supplies their inputs — named, not fabricated.

## Non-deltas

This vision admits nothing, spawns nothing, and grants no authority.
It is a Temple artifact proposing a shape; the shape was checked
against the committed graph law; the operator's GO is the only thing
that moves any lane from candidate to work.
