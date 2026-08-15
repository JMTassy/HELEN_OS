# GRAPH_DEPENDENCY_TRUTH — candidate doctrine

    STATUS = CANDIDATE_DOCTRINE
    AUTHORITY = false
    CANON = false
    LEDGER_EFFECT = none

Source: a public graph-engineering thread (Hanako, 11 août), read and
graded by the operator, who supplied five additions the source does
not contain. Encoded 2026-08-15 as `constitution/execution_graph.py`
(+25 tests, gate probe 97).

## The core claim

    edge(u, v)  iff  v actually consumes u's artifact or decision

Everything else in a diagram is typography, paid for in wall-clock
time. The scaling law follows:

    parallelism = independent executable work / false dependencies

Deleting false edges is usually more powerful than adding agents.

## The eight invariants (as encoded)

| # | invariant | executable refusal |
|---|---|---|
| 1 | Dependency truth | `E_FALSE_EDGE`, and the falsifier `E_HIDDEN_STATE` |
| 2 | Node contract (task/input/schema/named failures) | `E_UNCONTRACTED_NODE` |
| 3 | Four primitives CHAIN·FAN·ROUTER·CONTROLLED_CYCLE | `E_UNKNOWN_PRIMITIVE`, `E_UNCONTROLLED_CYCLE` |
| 4 | Join only when semantically required | `E_IMPLICIT_BARRIER` |
| 5 | Model judges; graph decides | `E_CLASSIFIER_MINTED_AUTHORITY`, `E_UNKNOWN_ROUTED_TO_DEFAULT` |
| 6 | Verification is an edge gate | `E_SELF_APPROVAL` |
| 7 | Durable referenced state | `E_TRANSCRIPT_PASSED`, `E_CONFLICTING_REWRITE`, `E_UNRESUMABLE_RUN` |
| 8 | Topology is economics | `E_UNPRICED_BREADTH`, `E_COUNT_BEFORE_SHAPE` |

## The operator's five additions (beyond the source)

1. **Structured output is insufficient without identity.**
   `O_n = (value, schema, producer, inputs, config, seq)` — two
   byte-identical JSONs produced under incompatible conditions are a
   `E_CONFIG_COLLISION`, not one artifact. *Deviation recorded:* the
   source's `timestamp` became a LOGICAL `seq`; wall-clock in the
   reducer zone breaks replay, and identity is done by
   (producer, inputs, config), not by the clock.
2. **`not_found` as a value is necessary but not sufficient.** Eight
   states, and `NOT_FOUND` (the world lacks it) is not `NO_ACCESS`
   (we could not look). Collapsing them routes blindness as absence.
3. **Joins need an explicit policy**, not "wait for results":
   CONTINUE if coverage ≥ τ · HOLD if evidence insufficient · FAIL on
   critical contradiction. 96 settled of 100 continue when the
   missing 4 are not required by the next decision.
4. **`100 agents ⊬ 100 independent evidence roots`** — the most
   important falsifier of the thread's slogan. Independence is a
   property of the evidence roots, not of the worker count.
5. **Topology controls more than tokens**: tail latency, permissions,
   error surface, tool contention, blast radius.

## Convergence with already-sealed kernel law (not novelty)

Addition 4 is the same theorem as `cross_model_independence.py`'s
`collapse_to_neff` and `scaling_harness.py`'s `swarm_common_mode`
(five same-config instances at T=0 → N_eff = 1), reached from a
different direction — swarm sampling there, graph fan-out here. The
convergence is worth recording precisely because it is NOT
independent evidence: one law, two statements, one root. Likewise
`E_SELF_APPROVAL` is the graph-layer instance of the debtor/creditor
law already at four levels (r* crossing, IAM, workflow approval,
bulla), and "model judges, graph decides" restates the OBLITERATUS
boundary where `compare_runs.py` may never emit PASS.

## The pipeline this licenses

    TASK → REAL DEPENDENCIES → GRAPH → CONTRACTS → AUTHORITY GATES
         → AGENT COUNT

never `TASK → "spawn 100 agents"` (`E_COUNT_BEFORE_SHAPE`). And the
promotion chain each transition must earn separately:

    GENERATION ≠ VERIFICATION ≠ ADMISSION ≠ PERSISTENCE ≠ TRUTH

`promotion_step("PERSISTENCE", "TRUTH")` refuses by name: the ledger
records what was admitted, not what is so.

## Falsifier (kept live)

> If removing an edge changes a downstream node despite that node
> consuming no upstream artifact or decision, hidden state exists and
> the graph contract is incomplete.

Encoded as `hidden_state_falsifier`: the observation refutes the
CONTRACT, not the law — which is what makes it a usable falsifier
rather than a slogan.

## Sizing

    N* = argmax_N [ V(coverage_N, quality_N)
                    − C_tokens − C_latency − C_coordination
                    − C_verification ]

Sometimes N* = 1. The test fixture demonstrates a value curve where
N* = 6 and N = 100 is strictly worse, and a second where N* = 1.
The cited "≈15× tokens" figure for multi-agent research is REPORTED
(secondary relay through the thread, not verified here) and is not
used as a kernel constant.

## Non-deltas

No agent was spawned; no graph was executed; no scheduler exists in
this repo. This module says which graphs are LICENSED. The doctrine
remains CANDIDATE at the operator's grade and mints no authority.
