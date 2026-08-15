"""WULMATH_TCB_ATTACK_V0 — red-team the admission seam. 🔵 OBSERVED · authority=false.

The Authority Non-Amplification theorem is CONDITIONAL on a Trusted Computing Base. Its interesting
security test is therefore not "can cognition hallucinate?" (it can, freely) but "can a worker path
violate an assumption H1–H5?". This module attacks each assumption and asserts the kernel resists,
in REACHABILITY form:

    ¬∃  σ₀ →_W σ₁ →_W … →_W σ_k   such that   A(σ_k) > A(σ₀)

i.e. no sequence composed only of worker-proposed transitions (a worker being any producer that
cannot name a recognized authority root) can reach a higher-authority state. The only state-changer
here is `apply_if_admitted` — every mutation is admission-gated; there is no un-gated σ writer (H1).

TCB boundary modeled: a worker may forge anything a witness carries EXCEPT membership in the kernel's
`RECOGNIZED_AUTHORITY_ROOTS` (the ρ_A resolver). `worker_can_name` makes that boundary explicit.
Determinism: pure.
"""
from __future__ import annotations

from typing import Dict, List, Mapping, Tuple

from helen_os.audit.wulmath_kernel import (
    A, COORDS, RECOGNIZED_AUTHORITY_ROOTS, AdmitResult, Witness, admit,
)

# a worker attempt: the coordinate changes it proposes + the witness it carries
Attempt = Tuple[Dict[str, int], Witness]


def worker_can_name(root: str) -> bool:
    """The ρ_A resolver's set is TCB-side. A worker can name arbitrary strings — never a recognized
    authority root. This is the modeled boundary of H4."""
    return root not in RECOGNIZED_AUTHORITY_ROOTS


def apply_if_admitted(state: Mapping[str, int], changes: Dict[str, int], witness: Witness):
    """The ONLY state-changer in this harness — every mutation crosses admit(). (H1: no direct write.)"""
    proposed = {**dict(state), **changes}
    res = admit(state, proposed, witness)
    if res.admitted:
        return proposed, res
    return dict(state), res


def run_worker_path(state0: Mapping[str, int], attempts: List[Attempt]):
    """Apply a sequence of worker attempts; return (final_state, trace, max_authority_reached)."""
    state = dict(state0)
    trace: List[AdmitResult] = []
    best = int(state.get(A, 0))
    for changes, witness in attempts:
        state, res = apply_if_admitted(state, changes, witness)
        trace.append(res)
        best = max(best, int(state.get(A, 0)))
    return state, trace, best


def max_authority_reachable(state0: Mapping[str, int], attempts: List[Attempt]) -> int:
    return run_worker_path(state0, attempts)[2]


# ── a library of adversarial worker attempts, one per assumption under attack ──
def attack_H2_smuggle_authority_with_epistemic_witness() -> Attempt:
    """H2 — Γ bypass: move A together with E. The witness is warranted for BOTH coordinates and
    carries a recognized authority root, so TypeOK and AuthorityOK would both pass — ONLY the domain
    clause can stop it. This isolates the shape rule: authority must move alone, whatever the witness."""
    return ({A: 1, "E": 1},
            Witness("dual", frozenset({"E", A}), epistemic_root="src-x", authority_root="ruling-1", wid="h2"))


def attack_H3_forge_verify_flag() -> Attempt:
    """H3 — verifier compromise: set valid=True by fiat on an authority-typed witness with a fake root.
    Even a compromised Verify cannot help, because ρ_A resolution is independent of Verify."""
    return ({A: 1}, Witness("self_verified", frozenset({A}), authority_root="i-say-so", valid=True, wid="h3"))


def attack_H4_forge_authority_root() -> Attempt:
    """H4 — witness forgery: a well-formed authority witness whose root the TCB does not recognize."""
    return ({A: 1}, Witness("forged", frozenset({A}), authority_root="forged-root", valid=True, wid="h4"))


def attack_H5_alternate_path_flood(n: int) -> List[Attempt]:
    """H5 — alternate authority path: flood the seam with n varied worker attempts (raise E/R/C/P
    freely, and repeatedly try to forge A). None may raise A."""
    out: List[Attempt] = []
    for i in range(n):
        coord = COORDS[i % 4]                       # cycle E,R,C,P — all worker-legal epistemic moves
        out.append(({coord: 1}, Witness("worker", frozenset({coord}), epistemic_root=f"src-{i}", wid=f"e{i}")))
        out.append(({A: 1}, Witness("worker_authority", frozenset({A}),
                                    authority_root=f"forged-{i}", valid=True, wid=f"a{i}")))
    return out
