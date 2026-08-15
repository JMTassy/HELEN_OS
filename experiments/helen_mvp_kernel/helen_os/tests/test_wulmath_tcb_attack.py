"""WULMATH_TCB_ATTACK_V0 — falsifiers for the conditional Authority Non-Amplification theorem. 🔵 OBSERVED.

THE CLAIM under test: under H1–H5 (no direct write, no Γ bypass, no verifier/resolver control, no
witness forgery, authority only through Γ), no worker-only path raises authority:
    ¬∃ σ₀ →_W … →_W σ_k with A(σ_k) > A(σ₀).
Each test attacks one assumption; the positive control confirms a TCB-issued authority witness DOES
raise A (so the harness is not vacuously blocking everything).
"""
from helen_os.audit.wulmath_kernel import (
    A, ADMIT, AUTHORITY_NOT_ROOTED, NOT_IN_DOMAIN, RECOGNIZED_AUTHORITY_ROOTS, Witness, admit,
)
from helen_os.audit.wulmath_tcb_attack import (
    apply_if_admitted, attack_H2_smuggle_authority_with_epistemic_witness,
    attack_H3_forge_verify_flag, attack_H4_forge_authority_root, attack_H5_alternate_path_flood,
    max_authority_reachable, run_worker_path, worker_can_name,
)


# ─────────── H1: the only state-changer is admission-gated ───────────
def test_H1_no_ungated_write_raises_authority():
    # apply_if_admitted is the sole mutator; a worker authority attempt with a forged root is not
    # admitted, so state (and A) is unchanged. There is no path around admit().
    state, res = apply_if_admitted({}, {A: 1}, Witness("w", frozenset({A}), authority_root="nope", wid="h1"))
    assert res.reason == AUTHORITY_NOT_ROOTED
    assert state.get(A, 0) == 0


# ─────────── H2: authority cannot be smuggled beside an epistemic change ───────────
def test_H2_gamma_shape_bypass_is_rejected():
    changes, wit = attack_H2_smuggle_authority_with_epistemic_witness()
    state, res = apply_if_admitted({}, changes, wit)
    assert res.reason == NOT_IN_DOMAIN          # A must move alone; {E,A} is not a licensed shape
    assert state.get(A, 0) == 0


# ─────────── H3: compromising Verify does not breach authority ───────────
def test_H3_forged_verify_flag_still_cannot_raise_authority():
    # the witness sets valid=True by fiat (a compromised Verify). ρ_A resolution is independent of
    # Verify, so the forged authority root is still rejected.
    changes, wit = attack_H3_forge_verify_flag()
    assert wit.valid is True                    # Verify "compromised"
    state, res = apply_if_admitted({}, changes, wit)
    assert res.reason == AUTHORITY_NOT_ROOTED
    assert state.get(A, 0) == 0


# ─────────── H4: a forged (non-recognized) authority root is rejected ───────────
def test_H4_forged_authority_root_rejected():
    changes, wit = attack_H4_forge_authority_root()
    state, res = apply_if_admitted({}, changes, wit)
    assert res.reason == AUTHORITY_NOT_ROOTED
    assert state.get(A, 0) == 0


def test_H4_worker_cannot_name_a_recognized_root():
    # the modeled TCB boundary: every recognized authority root is unnameable by a worker.
    assert all(not worker_can_name(r) for r in RECOGNIZED_AUTHORITY_ROOTS)
    assert worker_can_name("forged-root") and worker_can_name("i-say-so")


# ─────────── H5 / reachability theorem: no worker-only path raises authority ───────────
def test_H5_reachability_authority_never_rises_under_worker_flood():
    attempts = attack_H5_alternate_path_flood(500)      # 1000 attempts: 500 epistemic + 500 forged-A
    final, trace, best = run_worker_path({}, attempts)
    assert best == 0                                     # A(σ_k) never exceeds A(σ₀)=0
    assert final.get(A, 0) == 0
    # the epistemic moves DID land (non-vacuous: the seam admits legitimate worker proposals)
    assert any(r.reason == ADMIT for r in trace)
    # …and every A attempt was rejected for the authority clause
    assert all(r.reason == AUTHORITY_NOT_ROOTED for r in trace if A in r.changed)


def test_reachability_holds_regardless_of_worker_count():
    # N → arbitrarily large does not change the result (the point of the theorem).
    for n in (1, 50, 500):
        assert max_authority_reachable({}, attack_H5_alternate_path_flood(n)) == 0


# ─────────── positive control: the TCB path DOES raise authority ───────────
def test_positive_control_recognized_authority_witness_raises_authority():
    # a witness rooted in a TCB-recognized authority root admits ΔA — proving the harness is not
    # vacuously rejecting every authority transition.
    tcb_witness = Witness("operator_ruling", frozenset({A}), authority_root="ruling-1", wid="ok")
    state, res = apply_if_admitted({}, {A: 1}, tcb_witness)
    assert res.reason == ADMIT and state.get(A, 0) == 1
