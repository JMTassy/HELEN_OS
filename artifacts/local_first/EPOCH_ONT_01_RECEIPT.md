<!-- authority=false · claim=NO_CLAIM · non-sovereign sidecar · NOT a Γ admission -->
# EPOCH ONT-01 — LOCAL-METABOLISM RECEIPT

🔵 OBSERVED · NON_SOVEREIGN · authority=false · LEDGER_EFFECT=none
Runner: `tools/local_first_autoresearch.py` (propose→compress→WULmath→FABLE-prep)
Topic: *ontological promotion frontier: no representation inherits the status of its referent without a discharged crossing obligation*

## What this epoch IS — and is NOT
This is the **local-metabolism** loop, not the `EPIS-CYCLE` crossing pipeline. The
crossing runner your dispatch specified (`HAL_F/HAL_P/HAL_X · DISCRIMINATE ·
FrontierPacket · Γ · F*`) **does not exist in the SOT**: grep finds zero
`FrontierPacket / HAL_X / discharged_obligation / F_star / FAIL_UNLICENSED_FRONTIER`
in any `.py`/`.md`, and the commit reported to seal it — **`451ebf0` — is not a
known object in this repo** (it lives in the other session's unmerged worktree).
`NO INSTRUMENT = NO MEASUREMENT`.

## MEASURED (real, this run)
| metric | value |
|---|---|
| parse_yield (Gemma) | **12 / 12 = 1.0** — JSON array parsed clean, no FAILED_INVALID_JSON |
| CHIDDUSH candidates (Qwen) | 5 produced |
| local WULmath/schema valid | 5 / 5 |
| top survivor | `CHID-A7F291` |
| **independent provenance roots** | **1** — all candidates descend from ONE `gemma_propose()` call. `5 candidates ⊬ 5 witnesses`. |
| survivor status | 🟣 **CLAIM** · FABLE min-gate **PENDING** (input prepared, not gated) |

## NOT MEASURED — instrument absent (honest gap, not a result)
`HAL_F/HAL_P/HAL_X` · `DISCRIMINATE` · `FrontierPacket` · `Γ (HOLD/ADMIT/REJECT)` ·
`discharged_obligations` · `F*` · `FAIL_UNLICENSED_FRONTIER_MOVE`.
→ This runner has no Γ, so — correctly — **no admission receipt was emitted**
(your hard constraint "no receipt before Γ" is satisfied by emitting none).

## The experimental target could NOT be tested
```
ΔDischargedObligations = 0  ⇒  ΔF* = 0      → INSTRUMENT_UNRESOLVED (no F* in SOT)
+w_valid                    ⇒  F* may advance → INSTRUMENT_UNRESOLVED (no F* in SOT)
```
The frontier experiment requires the crossing instrument, which is **forked out
of the SOT**. It cannot be run here without laundering.

## Meta (the doctrine, live again)
Running *an* epoch did not produce the frontier measurement — `ran_a_runner ⊬
measured_the_frontier`. Possession of a run ⊬ measurement of crossing. Same shape
as UMS `Capability↑ ⊬ Authority↑`.

## Next (operator-gated)
- `RECONCILE` → merge the crossing worktree (where `451ebf0` + the 12-proposal
  pipeline live) into the SOT, so the real `EPIS-CYCLE` instrument exists here.
  **Then** the crossing epoch can run and F* can be honestly measured.
- `BUILD CROSSING` → wire `HAL_X/FrontierPacket/Γ/F*` into `experiments/helen_mvp_kernel/`.
- `GATE SURVIVOR` → paste `fable_min_gate_input.txt` to FABLE for the one-bit assay on CHID-A7F291.

*authority=false · non-sovereign · a run record, not a ruling.*
