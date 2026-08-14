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


# ─────────────────────────── FIXTURE 6 — warrant/value rebinding (I₆, FABLE swarm CHID-SMITH-1793) ───────────────────────────
def test_warrant_value_rebind_local_valid_global_invalid():
    # GAP WITNESS (preserved): before I₆ existed, the committed engine (I₁–I₅) ADMITTED this graph —
    # SIG_1 is minted on value X, then reused to bless value Y. The token is spent once, the graph is
    # acyclic, both claims ground to a root, no persistence, no effect conflict — all five gates are
    # BLIND to signature↔value integrity. The assertions below prove that blindness: only I₆ fires.
    g = (GraphIR()
         .add_node(Node("w", "Signer", root=True))
         .add_node(Node("a", "Claim asserting VALUE_X"))
         .add_node(Node("b", "Claim asserting VALUE_Y"))
         .add_edge(Edge("e1", "w", "a", EdgeType.DATA, warrant_binds=(("SIG_1", "VALUE_X"),)))
         .add_edge(Edge("e2", "w", "b", EdgeType.DATA, warrant_binds=(("SIG_1", "VALUE_Y"),))))
    violations = _local_all_valid_but_global_invalid(g, "E_WARRANT_VALUE_REBIND")
    # the witness: the five prior gates are SILENT on a graph that must be rejected → I₆ is a real gap
    for code in ("E_DOUBLE_SPEND", "E_PROVENANCE_CYCLE", "E_PROVENANCE_SELF_SUPPORT",
                 "E_UNWARRANTED_PERSISTENCE", "E_INCONSISTENT_EFFECT"):
        assert not any(code in x for x in violations), (code, violations)


def test_same_warrant_same_value_is_admissible():
    # guard: reusing a signature for the SAME value is honest re-attestation, not a rebind
    g = (GraphIR()
         .add_node(Node("w", "Signer", root=True))
         .add_node(Node("a", "A")).add_node(Node("b", "B"))
         .add_edge(Edge("e1", "w", "a", EdgeType.DATA, warrant_binds=(("SIG_1", "VALUE_X"),)))
         .add_edge(Edge("e2", "w", "b", EdgeType.DATA, warrant_binds=(("SIG_1", "VALUE_X"),))))
    ok, violations = g.global_validate()
    assert ok is True, violations


# ─────────────────────────── FIXTURE 7 — banishment: unrevoked capability (I₇) ───────────────────────────
def test_granted_capability_never_revoked_local_valid_global_invalid():
    # A privileged context (lease L) is opened but never torn down. Every edge is local-valid;
    # I₁–I₆ are silent (nothing double-spent, cyclic, rootless, persisted, conflicting, rebound) —
    # only banishment catches the dangling context. "Governed = provably closed."
    g = (GraphIR()
         .add_node(Node("open", "OpenContext"))
         .add_node(Node("act", "PrivilegedAction"))
         .add_edge(Edge("g1", "open", "act", EdgeType.CAPABILITY, grants=("lease_L",))))
    violations = _local_all_valid_but_global_invalid(g, "E_UNREVOKED_CAPABILITY")
    for code in ("E_DOUBLE_SPEND", "E_PROVENANCE_CYCLE", "E_PROVENANCE_SELF_SUPPORT",
                 "E_UNWARRANTED_PERSISTENCE", "E_INCONSISTENT_EFFECT", "E_WARRANT_VALUE_REBIND"):
        assert not any(code in x for x in violations), (code, violations)


def test_granted_and_revoked_capability_is_admissible():
    # open lease L, then provably close it (banishment) → clean teardown, admissible.
    g = (GraphIR()
         .add_node(Node("open", "OpenContext"))
         .add_node(Node("act", "PrivilegedAction"))
         .add_node(Node("close", "Teardown"))
         .add_edge(Edge("g1", "open", "act", EdgeType.CAPABILITY, grants=("lease_L",)))
         .add_edge(Edge("r1", "act", "close", EdgeType.CAPABILITY, revokes=("lease_L",))))
    assert g.all_edges_local_valid() is True
    ok, violations = g.global_validate()
    assert ok is True, violations                  # opened AND provably closed → admitted


def test_partial_revocation_flags_only_the_dangling_lease():
    g = (GraphIR()
         .add_node(Node("o", "O")).add_node(Node("a", "A"))
         .add_edge(Edge("g", "o", "a", EdgeType.CAPABILITY, grants=("L1", "L2")))
         .add_edge(Edge("r", "o", "a", EdgeType.CAPABILITY, revokes=("L1",))))   # L2 left open
    ok, violations = g.global_validate()
    assert ok is False
    assert any("L2" in x and "E_UNREVOKED_CAPABILITY" in x for x in violations)
    assert not any("'L1'" in x for x in violations)   # L1 was revoked — not flagged


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
