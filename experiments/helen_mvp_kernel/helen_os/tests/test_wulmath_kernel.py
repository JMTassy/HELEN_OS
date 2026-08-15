"""WULMATH_KERNEL_V0 — admission-calculus falsifiers. 🔵 OBSERVED.

THE LAW under test (stated first): Admit(δ)=1 ⟺ δ∈Dom(Γ) ∧ Verify ∧ TypeOK(coordinate-wise) ∧
AuthorityOK. The decisive claim is that a witness VALID for an epistemic change is REJECTED for an
authority change — capability ⊬ authority. Positive controls prove admission is not vacuously
always-False. Every test is derived from the law, not the law from the test.
"""
from helen_os.audit.wulmath_kernel import (
    A, C, E, P, R, X,
    ADMIT, AUTHORITY_NOT_ROOTED, NOT_IN_DOMAIN, WITNESS_INVALID, WITNESS_WRONG_TYPE,
    Witness, admit, authority_roots, derive, independent_evidence_count, swarm_has_authority,
)

# canonical witnesses
E_WIT = Witness("measurement", frozenset({E}), epistemic_root="src-1", wid="e1")
A_WIT = Witness("operator_ruling", frozenset({A}), authority_root="ruling-1", wid="a1")


# ─────────── the decisive pair: same-strength witness, different coordinate ───────────
def test_epistemic_witness_admits_epistemic_promotion():
    # positive control #1: admission actually WORKS for the right witness/coordinate pairing.
    res = admit({}, {E: 1}, E_WIT)
    assert res.admitted and res.reason == ADMIT and res.changed == frozenset({E})


def test_same_epistemic_witness_is_rejected_for_authority_promotion():
    # THE decisive test: the very witness that admitted ΔE cannot move ΔA. capability ⊬ authority.
    res = admit({}, {A: 1}, E_WIT)
    assert not res.admitted
    assert res.reason == WITNESS_WRONG_TYPE          # A ∉ warrant_coords(E_WIT)
    assert res.verified and not res.type_ok          # it verified — it was simply the wrong type


def test_authority_witness_admits_authority_promotion():
    # positive control #2: a properly authority-rooted witness DOES admit ΔA (non-vacuous).
    res = admit({}, {A: 1}, A_WIT)
    assert res.admitted and res.reason == ADMIT


# ─────────── AuthorityOK: authority must be rooted in ρ_A, never ρ_E ───────────
def test_authority_typed_but_epistemically_rooted_is_rejected():
    # AuthorityAssertion ∧ ρ_A=∅ ⇒ Reject — a distinct error class from a false claim.
    forged = Witness("claims_authority", frozenset({A}), epistemic_root="src-1", authority_root="", wid="f1")
    res = admit({}, {A: 1}, forged)
    assert not res.admitted
    assert res.type_ok and not res.authority_ok      # right type, but no authority root
    assert res.reason == AUTHORITY_NOT_ROOTED


def test_authority_root_must_resolve_not_merely_be_nonempty():
    # the ρ_A tightening: a non-empty but UNRECOGNIZED root is a forgery, rejected — before this
    # hardening a worker-named string would have admitted ΔA. This is the H4 boundary at kernel level.
    forged = Witness("forged_authority", frozenset({A}), authority_root="worker-forged", wid="wf1")
    res = admit({}, {A: 1}, forged)
    assert not res.admitted and res.reason == AUTHORITY_NOT_ROOTED


# ─────────── Dom(Γ): the forbidden-morphism table over shapes ───────────
def test_authority_and_effect_cannot_move_in_one_step():
    # Recommend ⊬ Authorize ⊬ Execute — each is its own gated transition.
    res = admit({}, {A: 1, X: 1}, A_WIT)
    assert not res.admitted and res.reason == NOT_IN_DOMAIN


def test_effect_requires_prior_authority():
    x_wit = Witness("effect_permit", frozenset({X}), wid="x1")
    assert admit({}, {X: 1}, x_wit).reason == NOT_IN_DOMAIN         # no prior authority → forbidden
    assert admit({A: 1}, {A: 1, X: 1}, x_wit).reason == ADMIT       # A already present → X alone admits


def test_promotions_only_no_silent_demotion():
    res = admit({E: 2}, {E: 1}, E_WIT)                              # a decrease is not in Dom(Γ) in V0
    assert not res.admitted and res.reason == NOT_IN_DOMAIN


def test_invalid_witness_fails_closed():
    invalid = Witness("measurement", frozenset({E}), epistemic_root="src-1", valid=False, wid="i1")
    res = admit({}, {E: 1}, invalid)
    assert not res.admitted and res.reason == WITNESS_INVALID


# ─────────── ρ_E root law (composed on epistemic_roots.n_epi): ΔD>0 ⊬ ΔE>0 ───────────
def test_derivation_never_adds_independent_evidence():
    derived = [derive(E_WIT, "summarize", f"d{i}") for i in range(1000)]
    assert independent_evidence_count([E_WIT] + derived) == 1        # 1001 representations, 1 root
    # control: a genuinely independent source DOES add a root
    other = Witness("measurement", frozenset({E}), epistemic_root="src-2", wid="e2")
    assert independent_evidence_count([E_WIT, other]) == 2


# ─────────── swarm non-amplification (TCB-relative): A(closure)=0 given ∀i A(Wᵢ)=0 ───────────
def test_swarm_of_epistemic_witnesses_has_no_authority():
    swarm = [Witness("worker", frozenset({E}), epistemic_root=f"src-{i}", wid=f"s{i}") for i in range(1000)]
    assert authority_roots(swarm) == frozenset()
    assert swarm_has_authority(swarm) is False
    # control: inject ONE real authority witness → authority appears (proves the check isn't inert)
    assert swarm_has_authority(swarm + [A_WIT]) is True
