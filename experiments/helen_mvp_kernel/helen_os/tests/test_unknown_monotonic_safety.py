"""UNKNOWN MONOTONIC SAFETY — falsifiers. 🔵 OBSERVED.

Capability↑ ⊬ Authority↑ · MORE-SEEN ⊬ MORE-CLAIMED · UNKNOWN is a valid terminal state.
STATIC: ¬V ⇒ UNKNOWN ∧ ¬Admit. DYNAMIC: adding a contradiction may lower the recommendation (ACT→HOLD),
i.e. ΔEvidence>0 ∧ ΔAuthority≤0. Adversarial: malformed · contradictory · partial · high-pressure.
"""
from helen_os.audit.ums import (
    DecisionSpec, Ev, Observation, Rec,
    admit, authority_rank, evidence_state, recommend,
)

# Decision fixture: should the territory deploy treatment system A?
SPEC = DecisionSpec("deploy treatment A",
                    required=("volume", "beach_access", "economics", "arsenic"))

def O(key, supported=True, contradicts=False):
    return Observation(key, supported=supported, contradicts=contradicts)

def full_support():
    return [O("volume"), O("beach_access"), O("economics"), O("arsenic")]


# ─────────────────────────── STATIC:  ¬V ⇒ UNKNOWN ∧ ¬Admit ───────────────────────────
def test_static_no_evidence_is_unknown_not_completion():
    assert recommend(SPEC, []) == Rec.UNKNOWN          # nothing observed → the bottom state, not a guess
    assert not admit(SPEC, [])                          # ¬V ⇒ ¬Admit

def test_static_partial_support_is_hold_never_act():
    obs = [O("volume"), O("beach_access")]              # economics + arsenic still UNKNOWN
    assert recommend(SPEC, obs) == Rec.HOLD
    assert not admit(SPEC, obs)

def test_static_full_support_admits_positive_control():
    assert recommend(SPEC, full_support()) == Rec.ACT   # non-vacuity: evidence DOES justify ACT
    assert admit(SPEC, full_support())


# ─────────────────────────── DYNAMIC: contradiction lowers authority (the teeth) ───────────────────────────
def test_dynamic_contradiction_flips_act_to_hold():
    before = full_support()
    after = before + [O("volume", contradicts=True)]    # ΔEvidence>0: a new contradicting source
    assert recommend(SPEC, before) == Rec.ACT
    assert recommend(SPEC, after) == Rec.HOLD           # R falls: ACT → HOLD
    assert authority_rank(SPEC, after) < authority_rank(SPEC, before)   # ΔAuthority < 0 under ΔEvidence > 0
    assert not admit(SPEC, after)                        # and it is de-admitted

def test_dynamic_more_evidence_more_unknown_is_allowed():
    # a run may end with MORE observations and LOWER authority — monotone exploration, non-monotone knowledge
    s_before = full_support()                            # ACT
    s_after = s_before + [O("arsenic", contradicts=True)]   # strictly more sources
    assert len(s_after) > len(s_before)
    assert authority_rank(SPEC, s_after) <= authority_rank(SPEC, s_before)

def test_dynamic_evidence_can_justify_a_rise():
    # the property is not "never rise" — supported evidence for a missing surface MAY raise HOLD→ACT
    partial = [O("volume"), O("beach_access"), O("economics")]   # arsenic UNKNOWN → HOLD
    complete = partial + [O("arsenic")]                          # now supported → ACT
    assert recommend(SPEC, partial) == Rec.HOLD
    assert recommend(SPEC, complete) == Rec.ACT
    assert authority_rank(SPEC, complete) > authority_rank(SPEC, partial)


# ─────────────────────────── ADVERSARIAL ───────────────────────────
def test_adv_high_pressure_prose_does_not_inflate():
    # 50 confident-but-UNSUPPORTED observations ("looks done") must not manufacture a claim
    pressure = [O("economics", supported=False) for _ in range(50)] + [O("arsenic", supported=False) for _ in range(50)]
    obs = [O("volume"), O("beach_access")] + pressure
    assert recommend(SPEC, obs) == Rec.HOLD             # economics/arsenic still UNKNOWN despite the flood
    assert not admit(SPEC, obs)                          # Goodhart guard: volume of prose ≠ support

def test_adv_contradiction_dominates_support():
    obs = [O("volume"), O("volume", contradicts=True)]  # same surface: supported AND contradicted
    assert evidence_state(SPEC, obs)["volume"] == Ev.CONTRADICTED
    assert recommend(SPEC, obs) == Rec.HOLD             # contradiction wins → never ACT

def test_adv_malformed_irrelevant_surface_has_no_effect():
    obs = full_support() + [O("unrelated_key"), O("", supported=True)]   # keys not in `required`
    assert recommend(SPEC, obs) == Rec.ACT             # ignored, cannot create or destroy support
    assert admit(SPEC, obs)

def test_adv_partial_with_one_contradiction_holds():
    obs = [O("volume"), O("beach_access"), O("economics", contradicts=True)]  # arsenic UNKNOWN + a contradiction
    assert recommend(SPEC, obs) == Rec.HOLD
    assert not admit(SPEC, obs)


# ─────────────────────────── THE SARGASSUM FIXTURE (operator's O1–O5) ───────────────────────────
def test_sargassum_o1_o4_holds_with_named_unknowns():
    # O1 volume ✓ · O2 access ✓ · O3 economics uncertain (unsupported) · O4 arsenic unresolved (unsupported)
    obs = [O("volume"), O("beach_access"), O("economics", supported=False), O("arsenic", supported=False)]
    st = evidence_state(SPEC, obs)
    assert recommend(SPEC, obs) == Rec.HOLD             # HOLD is a computational result, not an absence of one
    assert st["economics"] == Ev.UNKNOWN and st["arsenic"] == Ev.UNKNOWN   # the named unknowns survive
    assert not admit(SPEC, obs)

def test_sargassum_o5_contradiction_cannot_raise_authority():
    supported = [O("volume"), O("beach_access"), O("economics"), O("arsenic")]   # hypothetical full support → ACT
    with_o5 = supported + [O("volume", contradicts=True)]                        # O5 contradicts O1
    assert authority_rank(SPEC, with_o5) <= authority_rank(SPEC, supported)      # a new source never forces a stronger claim
    assert recommend(SPEC, with_o5) == Rec.HOLD


# ─────────────────────────── PEER-REVIEW REGRESSION GUARD ───────────────────────────
def test_contradiction_from_unknown_does_not_inflate_authority():
    # A pure counter-evidence source added to an all-UNKNOWN state must NOT raise committed authority.
    # (The earlier int(Rec) ranking wrongly raised rank 0→1 here — this locks the fix.)
    before, after = [], [O("volume", contradicts=True)]
    assert recommend(SPEC, before) == Rec.UNKNOWN
    assert recommend(SPEC, after) == Rec.HOLD                   # the VERDICT may shift UNKNOWN→HOLD (semantic)
    assert authority_rank(SPEC, before) == 0 and authority_rank(SPEC, after) == 0   # AUTHORITY must not rise
    assert authority_rank(SPEC, after) <= authority_rank(SPEC, before)


# ─────────────────────────── THE GLOBAL PROPERTY: coverage↑ ⊬ claims↑ ───────────────────────────
def test_coverage_grows_while_claims_do_not():
    # stream STARTS at the UNKNOWN bottom and grows only with contradictions / unsupported prose:
    # coverage strictly grows; committed authority (ACT) never rises above 0. Concrete check — no tautology.
    streams, cur = [], []
    for add in ([O("volume", contradicts=True)], [O("beach_access", supported=False)],
                [O("economics", contradicts=True)], [O("arsenic", supported=False)]):
        cur = cur + add
        streams.append(list(cur))
    sizes = [len(s) for s in streams]
    ranks = [authority_rank(SPEC, s) for s in streams]
    assert sizes == sorted(sizes) and sizes[-1] > sizes[0]      # coverage strictly grew
    assert ranks == [0, 0, 0, 0]                                # authority NEVER rose — non-vacuous
    assert all(ranks[i + 1] <= ranks[i] for i in range(len(ranks) - 1))   # monotone-non-increasing, real predicate
