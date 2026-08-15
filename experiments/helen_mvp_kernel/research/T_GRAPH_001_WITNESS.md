# T-GRAPH-001 — Graph Topology Audit v0.1 — witness

    STATUS = SPEC_CANDIDATE (operator's grade)
    AUTHORITY = false · CANON = false · LEDGER_EFFECT = none
    Kernel: graph_audit.py + obliteratus_graph_spec.py (+20 tests,
            gate 97->98), tip after commit of this doc.

The doctrine is now an executable admission gate. This is not "add
agents"; it is the missing layer between workflow design and the
worker runtime: **workers execute graphs; HELEN admits graphs.**

## The objective, enforced mechanically

    minimize CriticalPath(G')
    subject to   G' ≡_obs G               (observational equivalence)
    and          Authority(G') ⊆ Authority(G)

Both operator refinements are in force:

1. **Authority is never inherited.** Data/decision/control edges carry
   zero capability. `Authority(v) ⊆ Grant(v)`, and Grant changes only
   through an admitted `E_AUTHORITY`. A non-authority edge that tries
   to grant is `CAPABILITY_WITHOUT_GRANT`; an unadmitted authority
   edge is `INVALID_AUTHORITY_EDGE`. Dependency propagation ≠ privilege
   propagation.
2. **Equivalence is observational, not prose.** `observational_equivalence`
   compares schema · business_state · admitted_effects ·
   policy_decisions (equal) and required_evidence (after ⊇ before — the
   faster graph may not require *less* evidence). Cognitive prose may
   vary; exact output equality is the wrong test once cognition is
   probabilistic.

## The OBLITERATUS specimen — computed, not asserted

`obliteratus_graph_spec.py` types the audit's own workflow as
`G = (V, E, J, R, S, Π)`, in two forms: the naive `before` (targeted
tests chained, replays serial) and the audited `after` (targeted fan,
replays parallel). The auditor computed:

| metric | before | after |
|---|---|---|
| Critical path (CP) | **65** | **48** |
| Speedup | — | **17** |
| False DATA edges (F) | 4 | **0** |
| Max parallel width (W) | — | 4 |
| Authority surface (A) | 0 | **0** |
| Resume coverage (R) | — | 1.0 |
| Dependency precision (P) | — | 1.0 |
| Verification coverage (V) | — | 1.0 |
| Idempotent-effect coverage (I) | — | null* |

    GRAPH_VERDICT = PASS

*I is null, not zero: no node has an external side effect, so
idempotent-effect coverage is undefined — reported honestly rather
than as a misleading 0/0 = 0.

The four deleted false edges are exactly the "sequence mistaken for
dependency" cases: three serial edges chaining `TARGETED_1..4` (they
consume nothing from each other) and one edge forcing `REPLAY_2` to
wait on `REPLAY_1`. Deleting them is what turns CP 65 into 48. The
real dependency `COMPARE_RUNS → … → VERIFY_RECEIPT` is preserved, and
the replay join stays deterministic:

    J_replay = (required={r1, r2}, coverage=1.0, failure=HOLD,
                timeout=HOLD)

so `R1 exists ⊬ PASS` and no model judgement of "close enough"
satisfies the join.

## The three HOLD conditions, all tested

- **Authority expansion → HOLD.** Smuggle `prod.deploy` into the
  faster graph and the verdict flips to HOLD with
  `authority_expanded:prod.deploy`. A faster graph that widens
  capability is not an improvement.
- **Changed admitted effect → HOLD.** Move PASS-emission from
  VERIFY_RECEIPT to compare_runs in the observable contract and the
  equivalence test fails (`observational_divergence:admitted_effects`).
- **Errors present → optimization blocked.** `optimize_verdict`
  refuses before comparing metrics if the optimized graph has any
  hard error.

## Audit as a compiler pass

`Audit(G) = (errors, warnings, transformations, metrics)`. Ten hard
errors (cross-tenant state, model-controlled authority, capability
without grant, non-idempotent effect, missing admission boundary,
missing resume state, unbounded retry/fan, invalid authority edge,
state without owner) and eight structural warnings. Optimization is
permitted only when `errors == ∅`; warnings become *proposed*
transformations (`REMOVE_EDGE`, `STREAM_BRANCH`, `ARTIFACT_REFERENCE`,
`FAN_OUT`) — the compiler proposes, it never silently rewrites an
admitted graph.

Pipeline order is itself gated: `WORKFLOW → GRAPH_IR → DEPENDENCY_AUDIT
→ AUTHORITY_AUDIT → EFFECT_AUDIT → FAILURE_RESUME_AUDIT →
TOPOLOGY_OPTIMIZATION → OBSERVATIONAL_EQUIVALENCE → ADMISSION`.
Admitting before the audits is `E_ADMIT_BEFORE_AUDIT`; optimizing
before auditing is `E_OPTIMIZE_BEFORE_AUDIT`.

## Acceptance witness (files)

- `obliteratus/graph/graph_spec.json` — the admitted (after) graph +
  graph_hash.
- `obliteratus/graph/node_contracts.json` — every node's contract.
- `obliteratus/graph/topology_audit.json` — CP before/after, deleted
  false edges, fans, join policies, metrics, GRAPH_VERDICT=PASS.

## Self-caught during build (reported, not hidden)

My first test asserted 5 false edges; the auditor computed 4 — `(N-1)`
targeted serial edges + 1 replay serial = 3 + 1 = 4. The test was
wrong, the auditor was right; corrected to 4 with the arithmetic shown
in the test comment. The instrument caught its author.

## The law this freezes

    Parallelism is earned by proving independence.
    Speedup never licenses authority expansion.

## Non-deltas

No graph was executed; no worker was spawned; no scheduler exists.
This module decides which graphs are ADMISSIBLE. `I` coverage is
undefined here because OBLITERATUS has no external effects — the first
graph with a real side effect will exercise the idempotency/admission
-boundary errors that are already coded and tested on synthetic nodes.
Doctrine remains SPEC_CANDIDATE; nothing is admitted to canon.
