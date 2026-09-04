"""E011 — Warren quorum gate falsifiers. 🔵 OBSERVED.

Γ recomputes quorum from identity-bound ballots; a rogue Goblin gets no route from "impressive
aggregate object" to "the swarm approved this." Covers WQ-01..08 + the two critique gaps
(derived lineage WT-10, claim↔evidence binding WT-11) + quorum ⊬ ADMIT.
"""
from helen_os.warren.quorum import (
    APPROVE, REJECT, Ballot, CandidatePacket, EvidenceAtom, Outcome, Proposal,
    QuorumPolicy, ballot_message, gate, h_v, recompute_quorum, sign_ballot,
)

M = {"op": "config.set", "key": "x", "val": 1}
M_HASH = h_v(M)
SURFACE = h_v({"surface": "config"})
EPOCH = 7

ROSTER = QuorumPolicy(
    roster=(("g1", b"k1"), ("g2", b"k2"), ("g3", b"k3"), ("g4", b"k4")),
    threshold=3,
)
PGRAPH = {"root_a": "root_a", "root_b": "root_b", "root_c": "root_c"}


def _ballot(voter, policy=ROSTER, m=M_HASH, surface=SURFACE, epoch=EPOCH, vote=APPROVE, nonce="n"):
    b = Ballot(voter, m, surface, policy.policy_hash(), epoch, vote, nonce, sig="")
    key = policy.key_of(voter)
    return Ballot(voter, m, surface, policy.policy_hash(), epoch, vote, nonce, sign_ballot(b, key))


def _packet(ballots, claims=("config.set",), evidence=None):
    evidence = evidence or (EvidenceAtom("config.set", "L1", "root_a", "t1", "PASS"),)
    return CandidatePacket(claims=claims, evidence=evidence, ballots=tuple(ballots))


def _q(packet):
    return recompute_quorum(packet, ROSTER, M_HASH, SURFACE, EPOCH, PGRAPH)


# ---- WQ-01: one ballot, t=3 → no quorum
def test_wq01_single_ballot_below_threshold():
    assert not _q(_packet([_ballot("g1")])).quorum_met


# ---- WQ-02: duplicate voter_id cannot inflate count
def test_wq02_duplicate_voter_id_collapses():
    q = _q(_packet([_ballot("g1"), _ballot("g1"), _ballot("g1")]))
    assert q.approvals == 1 and not q.quorum_met     # set-cardinality on voter_id


# ---- WQ-03: ballots for a different H(M) don't count
def test_wq03_wrong_mutation_hash_rejected():
    bad = [_ballot("g1", m=h_v({"op": "EVIL"})), _ballot("g2"), _ballot("g3")]
    assert _q(_packet(bad)).approvals == 2           # g1's wrong-M ballot excluded → 2 < 3
    assert not _q(_packet(bad)).quorum_met


# ---- WQ-04: replayed epoch
def test_wq04_stale_epoch_rejected():
    stale = [_ballot("g1", epoch=EPOCH - 1), _ballot("g2"), _ballot("g3")]
    assert _q(_packet(stale)).approvals == 2         # stale ballot not counted


# ---- WQ-05: empty ballots (aggregate-only blob) cannot pass
def test_wq05_empty_ballots_no_quorum():
    assert not _q(_packet([])).quorum_met


# ---- WQ-06: t distinct valid APPROVE → quorum (but still ⊬ ADMIT, see below)
def test_wq06_threshold_distinct_approvals_meets_quorum():
    q = _q(_packet([_ballot("g1"), _ballot("g2"), _ballot("g3")]))
    assert q.quorum_met and q.approvals == 3


# ---- WQ-07: policy substitution (ballots signed under a different threshold/roster)
def test_wq07_policy_substitution_rejected():
    other = QuorumPolicy(roster=ROSTER.roster, threshold=2)   # different t → different policy_hash
    tampered = [
        Ballot("g1", M_HASH, SURFACE, other.policy_hash(), EPOCH, APPROVE, "n",
               sign_ballot(Ballot("g1", M_HASH, SURFACE, other.policy_hash(), EPOCH, APPROVE, "n", ""),
                           ROSTER.key_of("g1"))),
        _ballot("g2"), _ballot("g3"),
    ]
    # g1's ballot carries the wrong policy_hash for ROSTER → excluded → 2 < 3
    assert _q(_packet(tampered)).approvals == 2


# ---- WQ-08: cross-domain replay (valid HMAC but for a non-Warren message)
def test_wq08_cross_domain_replay_rejected():
    import hmac
    b = Ballot("g1", M_HASH, SURFACE, ROSTER.policy_hash(), EPOCH, APPROVE, "n", sig="")
    # sign a DIFFERENT-domain message with g1's key, then attach it to a Warren ballot
    foreign = hmac.new(ROSTER.key_of("g1"), h_v(["OTHER/DOMAIN", "g1"]).encode(), "sha256").hexdigest()
    forged = Ballot("g1", M_HASH, SURFACE, ROSTER.policy_hash(), EPOCH, APPROVE, "n", foreign)
    q = _q(_packet([forged, _ballot("g2"), _ballot("g3")]))
    assert q.approvals == 2                           # domain-separated msg ≠ forged sig


# ---- WT-10 (critique gap 1): forged declared lineages collapse to derived roots
def test_wt10_derived_lineage_not_declared():
    # 3 atoms with DIFFERENT declared_lineage but the SAME input_root → 1 derived lineage
    ev = (
        EvidenceAtom("config.set", "FAKE_L1", "root_a", "t1", "PASS"),
        EvidenceAtom("config.set", "FAKE_L2", "root_a", "t2", "PASS"),
        EvidenceAtom("config.set", "FAKE_L3", "root_a", "t3", "PASS"),
    )
    p = _packet([_ballot("g1"), _ballot("g2"), _ballot("g3")], evidence=ev)
    assert _q(p).independent_lineages == 1           # declared lineage ignored; root_a → 1


# ---- WT-11 (critique gap 2): claim without matching evidence is DIRTY (displacement blocked)
def test_wt11_claim_evidence_binding():
    p = CandidatePacket(
        claims=("RH_proved",),                       # claim...
        evidence=(EvidenceAtom("unrelated_test", "L1", "root_a", "t1", "PASS"),),  # ...unrelated evidence
        ballots=(_ballot("g1"), _ballot("g2"), _ballot("g3")),
    )
    outcome, reason = gate(p, ROSTER, M_HASH, SURFACE, EPOCH, PGRAPH)
    assert outcome == Outcome.REJECT and reason == "CLAIM_EVIDENCE_UNBOUND"


# ---- quorum ⊬ ADMIT: a met quorum yields a PROPOSAL (authority 0), never a capability
def test_e011_quorum_yields_proposal_not_authority():
    p = _packet([_ballot("g1"), _ballot("g2"), _ballot("g3")])
    outcome, obj = gate(p, ROSTER, M_HASH, SURFACE, EPOCH, PGRAPH)
    assert outcome == Outcome.PROPOSAL
    assert isinstance(obj, Proposal) and obj.authority == 0
    assert not hasattr(obj, "capability") and not hasattr(obj, "admitted")


# ---- NO_RECEIPT ≠ HOLD (distinct outcomes)
def test_e011_no_receipt_is_not_hold():
    p = _packet([_ballot("g1"), _ballot("g2"), _ballot("g3")])
    assert gate(p, ROSTER, M_HASH, SURFACE, EPOCH, PGRAPH, verification="ABSENT")[0] == Outcome.NO_RECEIPT
    assert gate(p, ROSTER, M_HASH, SURFACE, EPOCH, PGRAPH, jurisdiction="HUMAN")[0] == Outcome.HOLD


# ---- persona/narrative structurally cannot enter (no narrative field exists in the quotient)
def test_e011_narrative_has_no_channel():
    # two packets identical in ballots+evidence; there is NO persona/rhetoric field to differ on.
    p1 = _packet([_ballot("g1"), _ballot("g2"), _ballot("g3")])
    p2 = _packet([_ballot("g1"), _ballot("g2"), _ballot("g3")])
    assert gate(p1, ROSTER, M_HASH, SURFACE, EPOCH, PGRAPH)[1].__dict__ == \
           gate(p2, ROSTER, M_HASH, SURFACE, EPOCH, PGRAPH)[1].__dict__
