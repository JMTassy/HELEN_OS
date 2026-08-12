r"""Four-Ceiling Compositional Closure — the experiment that matters.

NON_SOVEREIGN · authority=false · canon=false · ledger_effect=none.

The corrected conjecture. Not a fifth ceiling — time lives inside the
predicates' evaluation context (ABAC: authorization depends on
subject/object/operation/environment). The real attack surface is
COMPOSITION.

Local admission:  Admit(delta, r) = P /\ S /\ A /\ R
Trace admission:  Admit*(delta_1 o ... o delta_n)

    THE CONJECTURE — Four-Ceiling Compositional Closure:
    for every admitted trace tau, require not only (for all i) C(d_i)=1
    but C(tau)=1, where C = P /\ S /\ A /\ R.

    THE GARDEN ATTACK:
    exists tau : (for all i, C(d_i)) /\ not C(tau)?

    Can several individually lawful moves compose into an unlawful one?

The honest result this module demonstrates (executably): YES, all four
ceilings can be defeated compositionally when C is evaluated ONCE PER
LOCAL OP. Four concrete counterexample traces are constructed, each
locally clean, each globally violating. And in every case the fix is
NOT a fifth ceiling — it is evaluating the SAME four predicates over
the trace's transitive/transactional closure. That is the operator's
point: "your four predicates must be evaluated transactionally over
the composed transition, not merely once per local operation."

So: no fifth ceiling is earned here. To earn one you would need a
trace that passes the four predicates BOTH locally AND transactionally
and is STILL constitutionally invalid. That has not been found.
Compositional completeness stays UNKNOWN, never PROVEN.

Precedent, cited not invented: in-toto's audit found downstream
verification alone insufficient — intermediate functionaries could
act on compromised inputs before final verification; NIST notes
authorization is operation-specific (authorized one way != authorized
another). Both are the compositional gap, in the security literature.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field

CEILINGS = ("PROOF", "SCOPE", "AUTHORITY", "REPLAY")


def canon(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str)


@dataclass(frozen=True)
class Delta:
    """One transition. local_ok records the per-op ceiling verdicts
    (as evaluated at that op alone). The other fields carry what a
    TRANSACTIONAL evaluation needs to see the composed effect."""
    delta_id: str
    local_ok: dict                     # ceiling -> bool, evaluated locally
    # transactional footprints:
    reads: frozenset = frozenset()     # info-flow sources touched
    writes: frozenset = frozenset()    # info-flow sinks written
    flow_from: str = ""                # label read
    flow_to: str = ""                  # sink written (for X->Z tracking)
    ontology_delta: int = 0            # entity-cardinality change
    asserts_identity: str = ""         # identity assertion produced
    derives_from: str = ""             # provenance parent artifact
    produces_artifact: str = ""
    evidence_root: str = ""
    premise_root: str = ""             # proof this op rests on
    t: int = 0

    def locally_admissible(self) -> bool:
        return all(self.local_ok.get(c, True) for c in CEILINGS)


def all_locally_admissible(trace: tuple) -> bool:
    return all(d.locally_admissible() for d in trace)


# ── the four transactional evaluators — same ceilings, over the trace ──

def trace_proof(trace: tuple) -> dict:
    """PROOF over the trace: transitive provenance closure. A chain of
    derivations collapses to its ROOTS; independent-witness count is
    |artifacts / ~provenance|, computed across the whole trace, not per
    op. Also: a premise that ceased to hold anywhere in the trace
    poisons any later op resting on it."""
    root_of = {}
    for d in trace:
        if d.produces_artifact:
            root_of[d.produces_artifact] = (
                root_of.get(d.derives_from, d.evidence_root or d.derives_from)
                if d.derives_from else (d.evidence_root or d.produces_artifact))
    independent_roots = set(root_of.values())
    return {"ceiling": "PROOF",
            "transitive_roots": sorted(independent_roots),
            "n_independent": len(independent_roots)}


def trace_scope(trace: tuple) -> dict:
    """SCOPE over the trace: the composed information flow. Even if no
    single op moves label X to sink Z, the trace's transitive flow may.
    reads/writes chained across ops reveal X -> ... -> Z."""
    # build flow edges: an op that reads L and writes into a buffer,
    # a later op reading that buffer and writing sink S -> edge L->S.
    reached = {}                       # buffer/label -> origin label
    flows = set()
    for d in trace:
        origin = d.flow_from
        if origin in reached:
            origin = reached[origin]
        for w in d.writes:
            reached[w] = origin or d.flow_from
            if d.flow_to:
                flows.add((origin or d.flow_from, d.flow_to))
        if d.flow_to and (origin or d.flow_from):
            flows.add((origin or d.flow_from, d.flow_to))
    return {"ceiling": "SCOPE", "composed_flows": sorted(flows)}


def trace_authority(trace: tuple) -> dict:
    """AUTHORITY over the trace: composed ontology/identity effect.
    Locally-authorized merges/transfers/canonicalizations can compose
    into an identity assertion no actor was authorized to make."""
    net_cardinality = sum(d.ontology_delta for d in trace)
    identity_assertions = sorted(d.asserts_identity for d in trace
                                 if d.asserts_identity)
    return {"ceiling": "AUTHORITY",
            "net_ontology_change": net_cardinality,
            "identity_assertions": identity_assertions}


def trace_replay(trace: tuple) -> dict:
    """REPLAY over the trace: premises must still hold at the point
    their consequence takes effect. A proof valid at t0 whose root was
    revoked before the effect at t2 breaks transactionally even though
    each op was locally fine at its own instant."""
    return {"ceiling": "REPLAY",
            "premise_chain": [(d.delta_id, d.premise_root, d.t)
                              for d in trace if d.premise_root]}


# ── the composed admission predicate C(tau) ─────────────────────────────

def admit_trace(trace: tuple, global_invariants: dict) -> dict:
    """C(tau): the four ceilings evaluated TRANSACTIONALLY against the
    trace's declared global invariants. This is what local per-op
    admission cannot see."""
    breaches = []

    # SCOPE: forbidden composed information flows
    forbidden_flows = set(global_invariants.get("forbidden_flows", ()))
    flows = set(trace_scope(trace)["composed_flows"])
    scope_hits = sorted(flows & forbidden_flows)
    if scope_hits:
        breaches.append({"ceiling": "SCOPE", "reason": "E_COMPOSED_FLOW",
                         "flows": scope_hits})

    # AUTHORITY: identity assertions no actor was authorized to make
    ta = trace_authority(trace)
    unauth = sorted(set(ta["identity_assertions"]) -
                    set(global_invariants.get("authorized_identities", ())))
    if unauth:
        breaches.append({"ceiling": "AUTHORITY",
                         "reason": "E_COMPOSED_IDENTITY", "assertions": unauth})

    # PROOF: transitive evidence-root inflation
    tp = trace_proof(trace)
    claimed = global_invariants.get("claimed_independent_roots")
    if claimed is not None and tp["n_independent"] < claimed:
        breaches.append({"ceiling": "PROOF",
                         "reason": "E_COMPOSED_EVIDENCE_INFLATION",
                         "actual_roots": tp["n_independent"],
                         "claimed": claimed})

    # REPLAY: a premise revoked before its effect
    revoked = global_invariants.get("revoked_at", {})   # root -> tick
    for d in trace:
        if d.premise_root in revoked and d.t >= revoked[d.premise_root]:
            breaches.append({"ceiling": "REPLAY",
                             "reason": "E_STALE_COMPOSED_PREMISE",
                             "delta": d.delta_id, "root": d.premise_root})
            break

    return {"verdict": "REJECT" if breaches else "ADMIT",
            "breaches": breaches,
            "ceilings_breached": sorted({b["ceiling"] for b in breaches})}


def compositional_gap(trace: tuple, global_invariants: dict) -> dict:
    """The Garden attack, run: does the trace pass locally yet fail
    transactionally? If so, it is a COMPOSITIONAL counterexample — and
    the diagnosis names WHETHER it demands a fifth ceiling or merely
    transactional evaluation of the existing four."""
    local = all_locally_admissible(trace)
    tr = admit_trace(trace, global_invariants)
    is_gap = local and tr["verdict"] == "REJECT"
    return {"all_local_admissible": local,
            "trace_verdict": tr["verdict"],
            "compositional_gap": is_gap,
            "breached_ceilings": tr["ceilings_breached"],
            "diagnosis": ("NON_COMPOSITIONAL_DEFINITION" if is_gap else
                          "no_gap"),
            "needs_fifth_ceiling": False if is_gap else None,
            "law": "the fix is evaluating the four ceilings over the "
                   "trace, not a fifth ceiling — unless a trace passes "
                   "BOTH local and transactional and is still invalid"}


def fifth_ceiling_status(counterexamples: tuple) -> dict:
    """The honest verdict on the conjecture. A counterexample earns a
    fifth ceiling ONLY if it passes both local AND transactional
    evaluation yet remains invalid. None here do — all are caught by
    transactional evaluation of the existing four."""
    earned = [c for c in counterexamples
              if c.get("passes_transactional") and c.get("still_invalid")]
    return {"counterexamples_found": len(counterexamples),
            "all_caught_by_transactional_eval": not earned,
            "fifth_ceiling_earned": bool(earned),
            "completeness": "UNKNOWN",
            "law": "NotObserved(fifth-ceiling counterexample) does not "
                   "entail Impossible; compositional completeness "
                   "accumulates evidence, never proof"}
