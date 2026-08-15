# T-GRAPH-002 — the machine-level graph contract

    STATUS = SPEC_CANDIDATE (operator's grade)
    AUTHORITY = false · CANON = false · LEDGER_EFFECT = none
    Artifacts: obliteratus/graph/{graph_ir.schema.json,
               audit_graph.py, obliteratus_v0.graph.json,
               topology_audit_v2.json}

The T-GRAPH-001 kernel proved the semantics; T-GRAPH-002 freezes them
as a machine-readable contract and a standalone static compiler.

## The architectural move: authority is manifest-assigned

    E_D transports data only
    Authority(v) ⊆ Grant(v)
    ΔGrant(v) != 0  ⇒  ∃ admitted e ∈ E_A

This closes an entire privilege-escalation family before runtime:
capability can never arrive along a data path. A node's effective
capabilities *equal* its own `grants`; the union of predecessors'
capabilities is not merely discouraged — it has no representation in
the IR at all. The only object that moves a capability is an admitted
`AUTHORITY` edge, recorded in the `grants` manifest with its
`admitted_by` (Gamma).

## The IR — five first-class objects + five contracts

`graph_ir.schema.json` (JSON Schema draft-07) defines:

- **Graph** — `id`, `version`, `state_owner` (the single durable-state
  owner; nodes never own persistent truth), nodes, edges, joins,
  routes, grants, observational_contract.
- **Node** — `id`, `kind`, `principal`, `consumes`, `produces`,
  `grants`, plus the contracts below.
- **Edge** — `type ∈ {DATA, DECISION, AUTHORITY, CONTROL}`;
  `artifact` for DATA, `grant`+`admitted` for AUTHORITY,
  `payload_kind` for transcript detection.
- **Join** — `required`, `coverage`, `on_failure`, `on_timeout`,
  `next_needs_complete_set`.
- **Grant** — `capability`, `to_node`, `via_edge`, `admitted_by`.

Supporting contracts: **EffectContract** (capability + idempotency_key
+ admission_boundary), **ResumeContract**, **VerifierContract**,
**AdmissionContract**, **ObservationContract**.

**Verification is a vector, never a boolean.** The VerifierContract
carries `producer_principal`, `verifier_principal`,
`producer_context_hash`, `verifier_context_hash`, `evidence_roots`,
`model_path`, `method`. Two differently named nodes sharing a context
hash still trip `MISSING_VERIFIER` — same distribution, same blind
spots. No single `independent: true` is accepted.

## The compiler — nine passes, in order

`audit_graph.py` runs, and refuses to reorder:

    PARSE → TYPECHECK → DEPENDENCY → AUTHORITY → EFFECT → RESUME →
    VERIFICATION → TOPOLOGY → OBSERVATIONAL_EQUIVALENCE

Optimization stops when `Errors(G) != ∅`. Ten hard errors
(CROSS_TENANT_STATE, MODEL_CONTROLLED_AUTHORITY, CAPABILITY_WITHOUT_GRANT,
INVALID_AUTHORITY_EDGE, MISSING_ADMISSION_BOUNDARY, NON_IDEMPOTENT_EFFECT,
MISSING_RESUME_STATE, UNBOUNDED_RETRY, UNBOUNDED_FAN, STATE_WITHOUT_OWNER);
eight warnings become **proposed** transformations only:

    CompilerProposal  !=>  GraphMutation

The compiler emits a candidate patch; Gamma still decides whether the
admitted graph changes. `audit_graph.py --selftest` fires all ten hard
errors on a crafted graph and drives the OBLITERATUS IR to PASS.

## The OBLITERATUS IR — the first compilation target

`obliteratus_v0.graph.json` is the audit's own workflow as IR, now
with a real effect node (`publish_result`: `grants:[audit.write]`,
`idempotency_key`, `admission_boundary:gamma`) fed by an admitted
authority edge `gamma → publish_result`. Compiled by `audit_graph.py`:

| metric | before | after |
|---|---|---|
| Critical path | **66** | **49** |
| Speedup | — | **17** |
| False DATA edges | 4 | **0** |
| Authority surface (A) | 1 | 1 |
| Idempotent-effect coverage (I) | — | **1.0** |
| Resume / precision / verification | — | 1.0 / 1.0 / 1.0 |

    GRAPH_VERDICT = PASS   (topology_audit_v2.json)

I is now 1.0 (not the kernel specimen's honest `null`) because the IR
carries a genuine effect node — `audit.write` is manifest-granted via
the admitted authority edge, holds an idempotency key, and names an
admission boundary. Smuggle a `prod.deploy` grant into the optimized
graph and the verdict flips to HOLD (`authority_expanded:prod.deploy`):
speedup never licenses authority expansion.

## Responsibility boundary (frozen)

    Workers execute nodes.
    The workflow engine owns durable state.
    Policy admits authority.
    HELEN admits graphs.

## L0 invariants

    Parallelism is earned by demonstrated independence.
    Parallelism may increase throughput; it may never increase authority.

## Note on the schema

`graph_ir.schema.json` is a real JSON Schema, but `audit_graph.py`
does NOT depend on a JSON-Schema validator library (stdlib only): its
PARSE/TYPECHECK pass hand-checks the structural invariants the schema
declares, so the auditor runs in any environment. The schema is the
human/interop contract; the compiler is the enforcement. Where they
could drift, the compiler is authoritative and the schema is
documentation — a divergence there is a bug to fix in the schema, not
a loophole in the gate.

## Non-deltas

No graph executed; no worker spawned; no scheduler exists. The
auditor is a static tool; its verdicts are re-derivable
(`--selftest`, deterministic). Doctrine remains SPEC_CANDIDATE.
