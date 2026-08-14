r"""TEST 1 — GlobalValidate consumes the ASSEMBLED GRAPH, not edges.

NON_SOVEREIGN · authority=false · canon=false · ledger_effect=none.

    A lawful institution is not a collection of lawful edges.
    Global composition itself has invariants.

The property under test, and the only one this module claims:

    for all e, LocalValid(e)  does not entail  GlobalValid(G)

graph_ir already names this refusal; nothing there EXECUTES it against
an assembled graph. This module is the checker, deliberately small:

    GlobalValidate(G) = AND_k I_k(G)

    I_1  for all kappa,  UseCount(kappa) <= 1
    I_2  the proof graph is foundationally acyclic
    I_3  no derivative provenance cycle mints a root
    I_4  temporal crossings carry persistence warrants

FIXTURE ORDER, as ruled. T_G1 first because it needs no semantic
interpretation at all:

    A --mint--> kappa       then TWO branches
    kappa --invoke--> E_1
    kappa --invoke--> E_2

Each edge alone satisfies everything a local validator can ask:
the capability exists, the scope is correct, the hash matches, the
effect is authorized. Composed:

    UseCount(kappa) = 2  >  1 = MaxUse(kappa)     =>  I_1 = FAIL

T_G2 and T_G3 follow, with the sharpened criteria:

    Roots(c) = {} AND DerivationSupport(c) != {}
        => FAIL_PROVENANCE_SELF_SUPPORT

targeting EPISTEMIC self-support rather than any structural cycle —
cycles across research epochs stay lawful (topology_rule), so "a cycle
exists" was the wrong predicate.

    State(t1) -> State(t2) AND W_persistence = {}
        => FAIL_TEMPORAL_PERSISTENCE

TWO NOTES ON THE RELAYED DEEP-KERNEL ENGINE, both checked in this
environment rather than asserted:

  - it does not import. `Dict[str, Any]` is annotated without `Any`
    imported and without `from __future__ import annotations`, so the
    class body raises NameError at definition time.
  - its acyclicity test is `max|eigenvalue| > 1e-5` on the adjacency
    matrix. The mathematics is right (a digraph is a DAG iff its
    adjacency matrix is nilpotent iff every eigenvalue is 0) but the
    numerics are the worst case for it: a nilpotent Jordan block has
    maximally ill-conditioned eigenvalues, and floating-point error of
    size d moves them by d^(1/n). Long DAGs are therefore reported
    CYCLIC. This module uses Kahn's algorithm in exact integer
    arithmetic instead — no floats, no numpy (which is not installed
    here anyway), and the answer is exact at every size.

STATUS DISCIPLINE. Passing a fixture licenses a claim about THAT
FIXTURE. The engine is PARTIALLY_WITNESSED, never verified.

Deterministic: no wall-clock, no randomness, canonical serialization.
"""
from __future__ import annotations

import json

MINT = "mint"
INVOKE = "invoke"
DERIVE = "derive"
PERSIST = "persist"
EDGE_KINDS = (MINT, INVOKE, DERIVE, PERSIST)

PASS = "PASS"
FAIL = "FAIL"
UNDEFINED = "UNDEFINED"

ROOT = "ROOT"
CLAIM = "CLAIM"

# a claim about a fixture is not a claim about the mechanism
VERIFIED_ON_EXECUTED_FIXTURE = "VERIFIED_ON_EXECUTED_FIXTURE"
PARTIALLY_WITNESSED = "PARTIALLY_WITNESSED"
REGISTERED_PRECLAIM_AGENDA = "REGISTERED_PRECLAIM_AGENDA"


def canon(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str)


# ── edges, and the LOCAL validator that will say PASS ──────────────────

def gedge(src: str, dst: str, kind: str, token: str | None = None,
          scope_ok: bool = True, hash_ok: bool = True,
          effect_authorized: bool = True, t_src: int = 0,
          t_dst: int = 0, persistence_warrant: bool = False,
          node_kind: str = CLAIM) -> dict:
    if kind not in EDGE_KINDS:
        return {"ok": False, "reason": "E_UNKNOWN_EDGE_KIND"}
    return {"ok": True, "src": src, "dst": dst, "kind": kind,
            "token": token, "scope_ok": scope_ok, "hash_ok": hash_ok,
            "effect_authorized": effect_authorized,
            "t_src": t_src, "t_dst": t_dst,
            "persistence_warrant": persistence_warrant,
            "node_kind": node_kind}


def local_validate(e: dict) -> dict:
    """Everything a validator can ask WITHOUT seeing the rest of the
    graph. This is the honest local checker — it must return PASS on
    the double-spend fixture, or the test would be vacuous."""
    if not e.get("ok"):
        return {"verdict": FAIL, "reason": e.get("reason")}
    fails = []
    if e["kind"] == INVOKE:
        if not e["token"]:
            fails.append("E_NO_CAPABILITY")
        if not e["scope_ok"]:
            fails.append("E_SCOPE")
        if not e["hash_ok"]:
            fails.append("E_HASH")
        if not e["effect_authorized"]:
            fails.append("E_UNAUTHORIZED_EFFECT")
    return {"verdict": FAIL if fails else PASS,
            "edge": f"{e['src']}->{e['dst']}", "reasons": fails,
            "scope": "this edge alone; no knowledge of siblings"}


# ── I_1: the affine capability ─────────────────────────────────────────

def use_count(edges: tuple, token: str) -> int:
    return sum(1 for e in edges
               if e.get("ok") and e["kind"] == INVOKE and
               e["token"] == token)


def I1_linear_capability(edges: tuple, max_use: int = 1) -> dict:
    """Girard's contraction axiom refused: C does not entail C tensor
    C. A capability is affine — minted once, spent at most once."""
    minted = sorted({e["token"] for e in edges
                     if e.get("ok") and e["kind"] == MINT and
                     e["token"]})
    over = {}
    for k in minted:
        n = use_count(edges, k)
        if n > max_use:
            over[k] = n
    return {"invariant": "I_1", "verdict": FAIL if over else PASS,
            "minted": minted,
            "use_counts": {k: use_count(edges, k) for k in minted},
            "max_use": max_use, "overspent": over,
            "reason": "CAPABILITY_DOUBLE_SPEND" if over else None,
            "law": "the contraction operator !C is forbidden; "
                   "consumption is destructive"}


# ── I_2: exact acyclicity, integer arithmetic only ─────────────────────

def _nodes(edges: tuple) -> tuple:
    seen = []
    for e in edges:
        for n in (e["src"], e["dst"]):
            if n not in seen:
                seen.append(n)
    return tuple(seen)


def I2_foundationally_acyclic(edges: tuple) -> dict:
    """Kahn's algorithm, exact. No eigenvalues, no tolerance, no
    floating point — a long DAG is a DAG at every size."""
    d = tuple(e for e in edges if e.get("ok") and e["kind"] == DERIVE)
    nodes = _nodes(d) if d else ()
    indeg = {n: 0 for n in nodes}
    for e in d:
        indeg[e["dst"]] += 1
    queue = [n for n in nodes if indeg[n] == 0]
    order = []
    while queue:
        n = queue.pop(0)
        order.append(n)
        for e in d:
            if e["src"] == n:
                indeg[e["dst"]] -= 1
                if indeg[e["dst"]] == 0:
                    queue.append(e["dst"])
    acyclic = len(order) == len(nodes)
    return {"invariant": "I_2",
            "verdict": PASS if acyclic else FAIL,
            "n_nodes": len(nodes), "topological_order": tuple(order),
            "reason": None if acyclic else "E_DERIVATION_CYCLE",
            "method": "Kahn, exact integer arithmetic",
            "law": "acyclicity is decided exactly; a nilpotent "
                   "adjacency matrix is the worst possible case for "
                   "floating-point eigenvalues"}


# ── I_3: epistemic self-support, not merely a cycle ────────────────────

def I3_no_self_supporting_root(edges: tuple, roots: frozenset) -> dict:
    """Roots(c) = {} AND DerivationSupport(c) != {} => FAIL.

    The sharpened criterion. A claim that HAS derivation support but
    can reach NO independent root is holding itself up. Structural
    cycles across research epochs stay lawful — 'a cycle exists' was
    the wrong predicate."""
    d = tuple(e for e in edges if e.get("ok") and e["kind"] == DERIVE)
    nodes = _nodes(d) if d else ()
    back = {n: [] for n in nodes}
    for e in d:
        back[e["dst"]].append(e["src"])
    bad = []
    for c in nodes:
        if not back[c]:
            continue                      # no support: not self-support
        seen, stack = set(), list(back[c])
        while stack:
            n = stack.pop()
            if n in seen:
                continue
            seen.add(n)
            stack.extend(back.get(n, []))
        if not (seen & set(roots)):
            bad.append(c)
    return {"invariant": "I_3", "verdict": FAIL if bad else PASS,
            "self_supporting_claims": tuple(sorted(bad)),
            "roots": tuple(sorted(roots)),
            "reason": "FAIL_PROVENANCE_SELF_SUPPORT" if bad else None,
            "law": "a claim with support but no reachable independent "
                   "root is holding itself up"}


# ── I_4: the connection; without it transport is UNDEFINED ─────────────

def I4_temporal_persistence(edges: tuple) -> dict:
    """State(t1) -> State(t2) with W_persistence = {} does not
    evaluate to FALSE — parallel transport without a connection is
    UNDEFINED. That is a HOLD, not a denial (guard_band)."""
    p = tuple(e for e in edges if e.get("ok") and e["kind"] == PERSIST)
    gaps = [f"{e['src']}->{e['dst']}" for e in p
            if e["t_dst"] > e["t_src"] and not e["persistence_warrant"]]
    return {"invariant": "I_4",
            "verdict": UNDEFINED if gaps else PASS,
            "unwarranted_crossings": tuple(gaps),
            "reason": "FAIL_TEMPORAL_PERSISTENCE" if gaps else None,
            "law": "without a connection the transport is undefined, "
                   "not false; HOLD rather than DENY"}


# ── I_5: warrant-value binding (CHID-SMITH-1793, witnessed gap) ────────

def _digest(value) -> str:
    import hashlib
    return hashlib.sha256(canon(value).encode()).hexdigest()[:16]


def mint_warrant(edge_ref: str, value) -> str:
    """A warrant is bound to (edge, value) at mint time. The binding
    travels inside the warrant string, so rebinding is detectable."""
    return f"warrant:{edge_ref}:{_digest(value)}"


def I5_warrant_binding(edges: tuple) -> dict:
    """Ghost/Shadow-Provenance, refused. A valid warrant reattached
    to a DIFFERENT value (or a different edge) passes every prior
    invariant: the token is spent once (I_1), the graph is acyclic
    (I_2), roots reach ground (I_3), transport is warranted (I_4) —
    and the reused signature launders value Y under value X's
    authority. Witnessed against this engine at commit 92f01d5:
    LOCAL PASS x4, GLOBAL PASS on a rebind graph. This invariant
    closes it: a warrant verifies only on the (edge, value) pair it
    was minted over."""
    bad = []
    for e in edges:
        if not e.get("ok"):
            continue
        w, v = e.get("warrant"), e.get("value")
        if w is None:
            continue                      # unwarranted edges are I_4's business
        expected = mint_warrant(f"{e['src']}->{e['dst']}", v)
        if w != expected:
            bad.append(f"{e['src']}->{e['dst']}")
    return {"invariant": "I_5", "verdict": FAIL if bad else PASS,
            "rebound_edges": tuple(bad),
            "reason": "E_WARRANT_VALUE_REBIND" if bad else None,
            "law": "a signature over value X reattached to value Y "
                   "is ghost provenance; the warrant binds the pair, "
                   "never the bearer"}


# ── GlobalValidate: consumes the assembled graph ───────────────────────

def global_validate(edges: tuple, roots: frozenset = frozenset(),
                    max_use: int = 1) -> dict:
    """AND_k I_k(G). Pure: reads the assembled graph, commits nothing.
    MUTATIONS_COMMITTED is 0 structurally, not by discipline."""
    if not edges:
        raise ValueError("E_EMPTY_GRAPH")
    locals_ = tuple(local_validate(e) for e in edges)
    invariants = (I1_linear_capability(edges, max_use),
                  I2_foundationally_acyclic(edges),
                  I3_no_self_supporting_root(edges, roots),
                  I4_temporal_persistence(edges),
                  I5_warrant_binding(edges))
    failed = [i for i in invariants if i["verdict"] == FAIL]
    undef = [i for i in invariants if i["verdict"] == UNDEFINED]
    verdict = FAIL if failed else (UNDEFINED if undef else PASS)
    return {"LOCAL_EDGE_RESULTS": tuple(l["verdict"] for l in locals_),
            "all_edges_locally_valid":
                all(l["verdict"] == PASS for l in locals_),
            "GLOBAL_RESULT": verdict,
            "REASON": (failed[0]["reason"] if failed else
                       (undef[0]["reason"] if undef else None)),
            "invariants": {i["invariant"]: i["verdict"]
                           for i in invariants},
            "detail": invariants,
            "MUTATIONS_COMMITTED": 0,
            "gap_witnessed": all(l["verdict"] == PASS
                                 for l in locals_) and verdict != PASS,
            "law": "GlobalValidate consumes the assembled graph, not "
                   "isolated edges"}


# ── the three fixtures ─────────────────────────────────────────────────

def fixture_double_spend() -> tuple:
    """T_G1. A --mint--> kappa ; kappa --invoke--> E_1 ; --invoke--> E_2."""
    return (gedge("A", "kappa", MINT, token="kappa"),
            gedge("kappa", "E_1", INVOKE, token="kappa"),
            gedge("kappa", "E_2", INVOKE, token="kappa"))


def fixture_honest_spend() -> tuple:
    """The positive control: one mint, one invoke. If this failed too,
    I_1 would be refusing the act rather than the double."""
    return (gedge("A", "kappa", MINT, token="kappa"),
            gedge("kappa", "E_1", INVOKE, token="kappa"))


def fixture_self_support() -> tuple:
    """T_G2. c1 -> c2 -> c3 -> c1, each derivation well-formed."""
    return (gedge("c1", "c2", DERIVE), gedge("c2", "c3", DERIVE),
            gedge("c3", "c1", DERIVE))


def fixture_grounded_chain() -> tuple:
    """The positive control for T_G2: same shape, real foundation."""
    return (gedge("r", "c1", DERIVE), gedge("c1", "c2", DERIVE),
            gedge("c2", "c3", DERIVE))


def fixture_warrant_rebind() -> tuple:
    """CHID-SMITH-1793. A warrant minted over value X on one edge,
    reused on another edge carrying value Y. Two clean mint/invoke
    pairs; every prior invariant passes; only the binding check
    refuses."""
    x = {"amount_state": "REQUESTED"}
    y = {"amount_state": "APPROVED"}
    e1 = gedge("kappa", "E_1", INVOKE, token="kappa")
    e1["value"], e1["warrant"] = x, mint_warrant("kappa->E_1", x)
    e2 = gedge("kappa2", "E_2", INVOKE, token="kappa2")
    e2["value"], e2["warrant"] = y, mint_warrant("kappa->E_1", x)
    return (gedge("A", "kappa", MINT, token="kappa"), e1,
            gedge("A2", "kappa2", MINT, token="kappa2"), e2)


def fixture_honest_warrant() -> tuple:
    """The positive control: same shape, each warrant minted over the
    value and edge it actually rides."""
    x = {"amount_state": "REQUESTED"}
    y = {"amount_state": "APPROVED"}
    e1 = gedge("kappa", "E_1", INVOKE, token="kappa")
    e1["value"], e1["warrant"] = x, mint_warrant("kappa->E_1", x)
    e2 = gedge("kappa2", "E_2", INVOKE, token="kappa2")
    e2["value"], e2["warrant"] = y, mint_warrant("kappa2->E_2", y)
    return (gedge("A", "kappa", MINT, token="kappa"), e1,
            gedge("A2", "kappa2", MINT, token="kappa2"), e2)


def fixture_temporal_gap() -> tuple:
    """T_G3. State(t1) -> State(t2) with no persistence warrant."""
    return (gedge("S_t1", "S_t2", PERSIST, t_src=1, t_dst=2,
                  persistence_warrant=False),)


def fixture_warranted_transport() -> tuple:
    return (gedge("S_t1", "S_t2", PERSIST, t_src=1, t_dst=2,
                  persistence_warrant=True),)


# ── status vocabulary, as ruled ────────────────────────────────────────

def fixture_status(engine_fixtures_passed: int,
                   engine_fixtures_total: int) -> dict:
    """Passing a fixture licenses a claim about that fixture. ADMITTED
    stays reserved for a real Gamma decision."""
    return {"TEST_FIXTURE": VERIFIED_ON_EXECUTED_FIXTURE,
            "ENGINE": PARTIALLY_WITNESSED,
            "fixtures_passed": engine_fixtures_passed,
            "fixtures_total": engine_fixtures_total,
            "delta_gamma": 0,
            "law": "a claim about a fixture is not a claim about the "
                   "mechanism"}


def registration(n_epochs: int, promotions: int) -> dict:
    """ADMITTED mixes two categories when no Gamma decision occurred."""
    if promotions > 0:
        return {"status": "E_UNWITNESSED_PROMOTION_CLAIM",
                "note": "a promotion count > 0 needs a Gamma decision "
                        "receipt, not an agenda entry"}
    return {"status": REGISTERED_PRECLAIM_AGENDA,
            "analytical_epochs": n_epochs, "delta_gamma": 0,
            "canon": False, "ledger_effect": "none",
            "law": "ADMITTED is reserved for a real Gamma decision"}


# ── two corrections carried into code ──────────────────────────────────

def attack_coverage(surfaces: tuple) -> dict:
    """Coverage_attack = |union_i S(HAL_i)|. Adding a redundant HAL may
    add no new surface, so N_HAL rising entails nothing."""
    union = set()
    for s in surfaces:
        union |= set(s)
    return {"n_HAL": len(surfaces),
            "coverage_attack": len(union),
            "union": tuple(sorted(union)),
            "N_HAL_entails_more_witness": False,
            "law": "N_HAL up does not entail N_witness up; coverage is "
                   "the union of attack surfaces, not the headcount"}


DECLARED_INTERFACE = ("candidate_hash", "contracted_data")
PROTECTED_SURFACE = ("policy_set", "evaluator", "required_warrants",
                     "admission_rules")


def undeclared_influence(proposer_writes: tuple) -> dict:
    """Influence_undeclared(Proposer, Discharger) = 0.

    Absolute zero influence is unimplementable — the discharger must
    read the proposed data. The property that bites is that the
    proposer touches nothing outside the declared interface."""
    breach = sorted(set(proposer_writes) & set(PROTECTED_SURFACE))
    undeclared = sorted(set(proposer_writes) - set(DECLARED_INTERFACE))
    return {"declared_interface": DECLARED_INTERFACE,
            "undeclared_writes": tuple(undeclared),
            "protected_surface_breached": tuple(breach),
            "influence_undeclared": len(undeclared),
            "ok": not undeclared,
            "reason": "E_UNDECLARED_INFLUENCE" if undeclared else None,
            "law": "the proposer may supply the candidate hash and "
                   "contracted data; it may not touch the policy set, "
                   "the evaluator, the required warrants or the "
                   "admission rules"}
