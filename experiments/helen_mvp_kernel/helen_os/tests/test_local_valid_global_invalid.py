"""Epoch-09 falsifier: ∀e LocalValid(e) ⊬ GlobalValid(G). 🔵 OBSERVED.

Each negative fixture asserts BOTH halves of the law: every edge passes the LOCAL
check AND the graph is globally REJECTED. The positive control asserts non-vacuity:
a genuinely valid graph must pass BOTH — otherwise a `global_validate` that always
returns False would satisfy every negative fixture for free.
"""
from helen_os.audit.graph_ir import EdgeType, Edge, GraphIR, Node


def _local_all_valid_but_global_invalid(g: GraphIR, expect_code: str):
    assert g.all_edges_local_valid() is True          # LEFT of the ⊬: every edge locally valid
    ok, violations = g.global_validate()
    assert ok is False                                 # RIGHT: graph globally rejected
    assert any(expect_code in v for v in violations), violations
    return violations


# ─────────────────────────── FIXTURE 1 — capability double-spend ───────────────────────────
def test_capability_double_spend_local_valid_global_invalid():
    g = (GraphIR()
         .add_node(Node("cap", "OneShotGrant"))
         .add_node(Node("A", "AgentA"))
         .add_node(Node("B", "AgentB"))
         .add_edge(Edge("e1", "cap", "A", EdgeType.CAPABILITY, consumes=("TOK_ONESHOT",)))
         .add_edge(Edge("e2", "cap", "B", EdgeType.CAPABILITY, consumes=("TOK_ONESHOT",))))
    _local_all_valid_but_global_invalid(g, "E_DOUBLE_SPEND")


# ─────────────────────────── FIXTURE 2 — provenance cycle ───────────────────────────
def test_provenance_cycle_local_valid_global_invalid():
    g = (GraphIR()
         .add_node(Node("c1", "Claim"))
         .add_node(Node("c2", "Claim"))
         .add_node(Node("w1", "Warrant"))
         .add_edge(Edge("e1", "c1", "c2", EdgeType.DERIVATION))
         .add_edge(Edge("e2", "c2", "w1", EdgeType.DERIVATION))
         .add_edge(Edge("e3", "w1", "c1", EdgeType.DERIVATION)))   # closes the loop
    _local_all_valid_but_global_invalid(g, "E_PROVENANCE_CYCLE")


# ─────────────────────────── FIXTURE 2b — provenance self-support (I₃, acyclic-yet-rootless) ───────────────────────────
def test_provenance_self_support_local_valid_global_invalid():
    # c1 → c2 is a clean DAG (no cycle → I₂ stays silent), but nothing is a primary root:
    # c2 has derivation support yet reaches no root. This is the orphan I₂ cannot see.
    g = (GraphIR()
         .add_node(Node("c1", "Hypothesis Alpha"))       # a claim, NOT a root
         .add_node(Node("c2", "Hypothesis Beta"))
         .add_edge(Edge("e1", "c1", "c2", EdgeType.DERIVATION)))
    violations = _local_all_valid_but_global_invalid(g, "E_PROVENANCE_SELF_SUPPORT")
    assert not any("E_PROVENANCE_CYCLE" in x for x in violations)   # isolation: acyclic, so I₂ must NOT fire


# ─────────────────────────── FIXTURE 3 — unwarranted temporal persistence ───────────────────────────
def test_temporal_persistence_local_valid_global_invalid():
    g = (GraphIR()
         .add_node(Node("s1", "AuthorizedState", t=100))
         .add_node(Node("s2", "AssumedState", t=200))
         .add_edge(Edge("e1", "s1", "s2", EdgeType.PERSISTENCE, warrants=())))  # no W_persistence
    _local_all_valid_but_global_invalid(g, "E_UNWARRANTED_PERSISTENCE")


# ─────────────────────────── FIXTURE 4 — mutually inconsistent effects ───────────────────────────
def test_inconsistent_effects_local_valid_global_invalid():
    g = (GraphIR()
         .add_node(Node("trig", "Trigger"))
         .add_node(Node("e_true", "SetTrue", mutates=("LEDGER_LOCK", "TRUE")))
         .add_node(Node("e_false", "SetFalse", mutates=("LEDGER_LOCK", "FALSE")))
         .add_edge(Edge("e1", "trig", "e_true", EdgeType.EFFECT))
         .add_edge(Edge("e2", "trig", "e_false", EdgeType.EFFECT)))
    _local_all_valid_but_global_invalid(g, "E_INCONSISTENT_EFFECT")


# ─────────────────────────── POSITIVE CONTROL — non-vacuity ───────────────────────────
def test_valid_graph_is_globally_admissible():
    # a clean graph: acyclic derivation · one token consumed once · warranted persistence · one effect.
    # global_validate MUST accept it, or every negative fixture above passes vacuously.
    g = (GraphIR()
         .add_node(Node("src", "Source", t=0, root=True))   # primary provenance root
         .add_node(Node("mid", "Derived", t=1))
         .add_node(Node("cap", "Grant", t=1))
         .add_node(Node("act", "Action", t=1))
         .add_node(Node("s1", "State", t=10))
         .add_node(Node("s2", "State", t=20))
         .add_node(Node("eff", "Effect", t=2, mutates=("MODE", "ON")))
         .add_edge(Edge("d1", "src", "mid", EdgeType.DERIVATION))
         .add_edge(Edge("c1", "cap", "act", EdgeType.CAPABILITY, consumes=("TOK_A",)))
         .add_edge(Edge("p1", "s1", "s2", EdgeType.PERSISTENCE, warrants=("W_persist_1",)))
         .add_edge(Edge("f1", "src", "eff", EdgeType.EFFECT)))
    assert g.all_edges_local_valid() is True
    ok, violations = g.global_validate()
    assert ok is True, violations          # non-vacuity: a valid graph is admitted
    assert violations == []


def test_two_distinct_tokens_do_not_false_trip_double_spend():
    # guard: distinct one-shot tokens consumed once each is NOT a double-spend
    g = (GraphIR()
         .add_node(Node("cap", "Grant")).add_node(Node("A", "A")).add_node(Node("B", "B"))
         .add_edge(Edge("e1", "cap", "A", EdgeType.CAPABILITY, consumes=("TOK_A",)))
         .add_edge(Edge("e2", "cap", "B", EdgeType.CAPABILITY, consumes=("TOK_B",))))
    ok, violations = g.global_validate()
    assert ok is True, violations
