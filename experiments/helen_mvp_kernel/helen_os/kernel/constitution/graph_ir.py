r"""HELEN_GRAPH_IR_V0 — the typed institutional runtime, as an IR.

NON_SOVEREIGN · authority=false · canon=false · ledger_effect=none.

Not new doctrine: a compilation of laws already enforced elsewhere in
this constitution into a small typed intermediate representation, so
the runtime can never INFER a relation it was not given.

    Graph Engineering = dependency topology
    HELEN             = dependency topology
                      + epistemic typing
                      + authority typing
                      + proof-carrying transitions

THE EDGE IS THE CONSTITUTIONAL OBJECT. Classical graph engineering
reads an edge as "B reads A's output". Here an edge is a morphism
under contract:

    e = (src, dst, lambda, dP, dA, dE, witness)

with the HARD DEFAULT

    dP = dA = dE = 0        communication is NON-PROMOTIONAL

An edge that cannot exhibit what epistemic state, provenance,
permission or witness it transfers is constitutionally PAINTED ON —
the governed reading of "if the next worker never reads the bucket,
the rope is painted on".

ONE TYPED MULTIGRAPH, not three graphs: lambda(e) in {DATA,
DERIVATION, AUTHORITY, EFFECT}. The same node pair may carry several
relations; the type is explicit precisely so the runtime can never
infer DATA => AUTHORITY.

THREE STATIC CHECKS (compile time):

    DATA       does not entail  PROOF
    PROOF      does not entail  AUTHORITY
    AUTHORITY  does not entail  EFFECT

ONE DYNAMIC CHECK (run time) — the one that upgrades an orchestrator
into a typed institutional runtime:

    (for all n_i: locally admissible)  does not entail
    G globally admissible

Detecting the fourth is the whole difference. The instance shipped
here is the root-multiplication attack: every worker edge is locally
lawful and preserves its root, and the merge still reports N roots.

HOLD IS PRODUCTIVE, not a dead end:

    u = (question, missing_witness, discriminator, cost,
         authority_required)
    G_{t+1} = G_t + Edges(Unresolved(G_t))

The graph self-generates its next experiments from its own gaps.

TOPOLOGY, corrected: within ONE admission transaction the graph is a
DAG. ACROSS research epochs cycles are lawful (hypothesis ->
experiment -> update -> new hypothesis). Episodes must be acyclic and
replayable; the research process need not be.

Deterministic: no wall-clock, no randomness, canonical serialization.
"""
from __future__ import annotations

import json

EDGE_TYPES = ("DATA", "DERIVATION", "AUTHORITY", "EFFECT")

STATIC_CHECKS = (("DATA", "PROOF"),
                 ("PROOF", "AUTHORITY"),
                 ("AUTHORITY", "EFFECT"))


def canon(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str)


# ── the edge: a morphism under contract ────────────────────────────────

def edge(src: str, dst: str, lam: str, dP: int = 0, dA: int = 0,
         dE: int = 0, witness: str | None = None,
         root: str | None = None) -> dict:
    """Build one typed edge. Any non-zero delta must exhibit its
    witness; a DATA edge may never carry authority or effect."""
    if lam not in EDGE_TYPES:
        return {"ok": False, "reason": "E_UNKNOWN_EDGE_TYPE"}
    if (dP or dA or dE) and not witness:
        return {"ok": False, "reason": "E_UNWITNESSED_PROMOTION",
                "law": "communication is non-promotional by default; "
                       "a delta must exhibit its witness"}
    if lam == "DATA" and (dA or dE):
        return {"ok": False, "reason": "E_DATA_EDGE_CARRIES_AUTHORITY",
                "law": "the type is explicit so the runtime can never "
                       "infer DATA => AUTHORITY"}
    return {"ok": True, "src": src, "dst": dst, "lambda": lam,
            "dP": dP, "dA": dA, "dE": dE, "witness": witness,
            "root": root}


def painted_on(e: dict) -> dict:
    """An edge that transfers nothing it can name is decoration."""
    if not e.get("ok"):
        return {"painted_on": None, "reason": e.get("reason")}
    carries = bool(e["dP"] or e["dA"] or e["dE"] or
                   e["lambda"] == "DATA" and e.get("root"))
    return {"painted_on": not carries,
            "law": "an edge that cannot exhibit what state, "
                   "provenance, permission or witness it transfers is "
                   "constitutionally painted on"}


# ── the three static checks ────────────────────────────────────────────

def static_check(premise: str, conclusion: str) -> dict:
    """Compile-time refusal of the three inferences."""
    if (premise, conclusion) in STATIC_CHECKS:
        return {"licensed": False,
                "reason": f"E_{premise}_DOES_NOT_ENTAIL_{conclusion}"}
    return {"licensed": None, "note": "not one of the three named "
                                      "static forms"}


def compile_graph(edges: tuple) -> dict:
    """Static pass: every edge well-typed, no inferred promotions."""
    bad = [e for e in edges if not e.get("ok")]
    if bad:
        return {"compiles": False, "reason": bad[0]["reason"]}
    painted = [f"{e['src']}->{e['dst']}" for e in edges
               if painted_on(e)["painted_on"]]
    return {"compiles": True, "n_edges": len(edges),
            "painted_on_edges": painted,
            "static_checks_enforced": len(STATIC_CHECKS)}


# ── the fourth: the dynamic check ──────────────────────────────────────

def globally_admissible(edges: tuple, merge_root_count: int) -> dict:
    """Every edge locally lawful does NOT entail the graph lawful.
    The shipped instance: N worker edges each preserving one root,
    and a merge that reports N. Locally clean, globally laundering."""
    if not edges:
        raise ValueError("E_EMPTY_GRAPH")
    locally = all(e.get("ok") for e in edges)
    true_roots = len({e.get("root") for e in edges
                      if e.get("root") is not None})
    inflated = merge_root_count > true_roots
    return {"all_locally_admissible": locally,
            "true_independent_roots": true_roots,
            "merge_reported_roots": merge_root_count,
            "globally_admissible": locally and not inflated,
            "reason": "E_ROOT_INFLATION_AT_MERGE" if inflated else None,
            "gap_detected": locally and inflated,
            "law": "for all n_i locally admissible does not entail G "
                   "globally admissible; detecting this is what makes "
                   "a typed institutional runtime"}


# ── HOLD as a productive object ────────────────────────────────────────

HOLD_FIELDS = ("question", "missing_witness", "discriminator", "cost",
               "authority_required")


def hold(**u) -> dict:
    """A HOLD that cannot name its missing witness is an impasse, not
    an obligation."""
    missing = [k for k in HOLD_FIELDS if k not in u]
    if missing:
        return {"ok": False, "reason": "E_UNTYPED_HOLD",
                "missing": sorted(missing)}
    return {"ok": True, **{k: u[k] for k in HOLD_FIELDS}}


def expand_graph(edges: tuple, holds: tuple) -> dict:
    """G_{t+1} = G_t + Edges(Unresolved(G_t)). The graph generates its
    own next experiments from its own gaps."""
    typed = [h for h in holds if h.get("ok")]
    untyped = len(holds) - len(typed)
    new = tuple(edge(f"hold:{h['question'][:24]}", h["discriminator"],
                     "DATA", root=None) for h in typed)
    return {"acquisition_edges_added": len(new),
            "untyped_holds_refused": untyped,
            "G_next_size": len(edges) + len(new),
            "law": "uncertainty becomes a scientific backlog, not a "
                   "dead end"}


# ── topology: DAG per transaction, cycles across epochs ────────────────

def topology_rule(scope: str) -> dict:
    if scope == "admission_transaction":
        return {"scope": scope, "must_be_acyclic": True,
                "replayable": True}
    if scope == "research_epochs":
        return {"scope": scope, "must_be_acyclic": False,
                "cycles_lawful": True,
                "example": "hypothesis -> experiment -> update -> "
                           "new hypothesis"}
    return {"scope": scope, "reason": "E_UNKNOWN_SCOPE"}
