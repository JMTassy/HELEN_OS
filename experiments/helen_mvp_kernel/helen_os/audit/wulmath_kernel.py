"""WULMATH_KERNEL_V0 — the proof-carrying admission calculus. 🔵 OBSERVED · authority=false.

HELEN's trusted seam is small: it does not ask whether a proposal is true or well-argued, it
asks whether THIS witness licenses THIS precise difference between two institutional states.

THE ADMISSION LAW (written first; the tests are derived from it):

    Admit(δ) = 1  ⟺  δ∈Dom(Γ)  ∧  Verify(w,δ)  ∧  TypeOK(w,Δσ)  ∧  AuthorityOK(w,ΔA)

    δ∈Dom(Γ)        the transition SHAPE is a licensed morphism (authority moves alone; an
                    effect requires prior authority; promotions only — the forbidden-morphism table)
    Verify(w,δ)     the witness actually attests this operation
    TypeOK(w,Δσ)    COORDINATE-WISE: every changed coordinate k has k ∈ warrant_coords(w).
                    A witness valid for an epistemic change (ΔE) is REJECTED for an authority
                    change (ΔA). This is the clause that makes it a kernel, not a slogan.
    AuthorityOK     if ΔA≠0, w must be rooted in authority provenance ρ_A — never ρ_E.
                    AuthorityAssertion ∧ ρ_A=∅ ⇒ Reject (a distinct error class from "false claim").

Consequences made executable:
    capability scaling ⊬ authority scaling        ExecOK ⊬ Admissible
    ΔD>0 ⊬ ΔE>0   (derivation grows; independent evidence does not — composed on epistemic_roots.n_epi)
    A(closure(W₁..Wₙ))=0 given ∀i A(Wᵢ)=0         (swarm non-amplification, TCB-relative)

TCB caveat (honest): these hold only while workers cannot write σ directly, cannot modify Γ /
Verify / ρ_A, and cannot forge a recognised authority root. This module IS a piece of that TCB —
small, deterministic, pure — not a proof that the surrounding system enforces the caveat.
Determinism: pure.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, FrozenSet, Iterable, Mapping, Tuple

from helen_os.audit.epistemic_roots import Representation, n_epi

# ── the institutional state coordinates σ = (E,R,C,P,A,X) ──
E, R, C, P, A, X = "E", "R", "C", "P", "A", "X"
COORDS: Tuple[str, ...] = (E, R, C, P, A, X)
#   E epistemic/evidence · R representation · C claim · P permission/capability · A authority · X effect

State = Mapping[str, int]        # coordinate → promotion level (default 0)

# admission verdict reason codes (fail-closed)
NOT_IN_DOMAIN = "NOT_IN_DOMAIN"
WITNESS_INVALID = "WITNESS_INVALID"
WITNESS_WRONG_TYPE = "WITNESS_WRONG_TYPE"
AUTHORITY_NOT_ROOTED = "AUTHORITY_NOT_ROOTED"
ADMIT = "ADMIT"


@dataclass(frozen=True)
class Witness:
    """A proposed justification. It carries no force until the admission calculus runs on it."""
    kind: str
    warrant_coords: FrozenSet[str]      # which coordinates this witness is TYPE-appropriate for
    epistemic_root: str = ""            # ρ_E root id ("" ⇒ none)
    authority_root: str = ""            # ρ_A root id ("" ⇒ none) — must be distinct provenance from ρ_E
    valid: bool = True                  # Verify(w,δ): does it actually attest the operation?
    wid: str = ""                       # witness identity (for derivation bookkeeping)


@dataclass(frozen=True)
class AdmitResult:
    admitted: bool
    in_domain: bool
    verified: bool
    type_ok: bool
    authority_ok: bool
    reason: str
    changed: FrozenSet[str]


def _delta(before: State, proposed: State) -> Dict[str, int]:
    return {k: int(proposed.get(k, 0)) - int(before.get(k, 0)) for k in COORDS}


def _in_domain(before: State, delta: Dict[str, int], changed: FrozenSet[str]) -> bool:
    """Dom(Γ): the forbidden-morphism table over transition SHAPES.

    - at least one coordinate changes and all changes are promotions (Δ ≥ 0);
    - authority moves ALONE — Recommend ⊬ Authorize is a separate gated step;
    - an effect moves alone and only when authority already exists (A_before > 0) — Authorize ⊬ Execute;
    - all other promotions live in the epistemic/representation/claim/permission block.
    """
    if not changed:
        return False
    if any(v < 0 for v in delta.values()):        # promotions only in V0 (teardown is a different op)
        return False
    if A in changed:
        return changed == {A}
    if X in changed:
        return changed == {X} and int(before.get(A, 0)) > 0
    return changed <= {E, R, C, P}


def _type_ok(witness: Witness, changed: FrozenSet[str]) -> bool:
    """Coordinate-wise: the witness must be type-appropriate for EVERY coordinate it moves."""
    return all(k in witness.warrant_coords for k in changed)


# ρ_A resolver — the authority-provenance roots the TCB recognizes. This set is part of the trusted
# computing base; a worker cannot enlarge it, so a witness whose authority_root is not in it is a
# forgery however well-formed. This is the H4 (witness-forgery) defense: a non-empty string is NOT
# enough — the root must actually RESOLVE. Workers may name arbitrary strings, never these.
RECOGNIZED_AUTHORITY_ROOTS: FrozenSet[str] = frozenset({"operator-genesis", "ruling-1"})


def authority_root_recognized(root: str) -> bool:
    """ρ_A(w) reaches a recognized authority root. TCB-side; not worker-controllable."""
    return root in RECOGNIZED_AUTHORITY_ROOTS


def _authority_ok(witness: Witness, delta: Dict[str, int]) -> bool:
    """If authority changes, the witness must be rooted in authority provenance ρ_A AND that root
    must RESOLVE through the TCB's recognized-root set. An epistemic root never suffices; neither
    does a forged (non-recognized) authority root — that is the H4 boundary."""
    if delta.get(A, 0) == 0:
        return True
    return authority_root_recognized(witness.authority_root)


def admit(before: State, proposed: State, witness: Witness) -> AdmitResult:
    """The four-clause admission predicate. Fail-closed; reports the first clause that fails."""
    delta = _delta(before, proposed)
    changed = frozenset(k for k in COORDS if delta[k] != 0)

    in_dom = _in_domain(before, delta, changed)
    verified = bool(witness.valid)
    type_ok = _type_ok(witness, changed)
    authority_ok = _authority_ok(witness, delta)

    if not in_dom:
        reason = NOT_IN_DOMAIN
    elif not verified:
        reason = WITNESS_INVALID
    elif not type_ok:
        reason = WITNESS_WRONG_TYPE
    elif not authority_ok:
        reason = AUTHORITY_NOT_ROOTED
    else:
        reason = ADMIT

    return AdmitResult(
        admitted=(reason == ADMIT),
        in_domain=in_dom, verified=verified, type_ok=type_ok, authority_ok=authority_ok,
        reason=reason, changed=changed)


# ── ρ_E root law: derivation grows the derivation count, never the independent-evidence count ──
def derive(witness: Witness, op: str, wid: str) -> Witness:
    """A derivation (summarize / translate / vote / RAG / paraphrase / ensemble) yields a NEW
    representation sharing the SAME epistemic root and carrying NO authority — ΔD>0, ΔE=0."""
    return Witness(kind=f"derived:{op}", warrant_coords=witness.warrant_coords,
                   epistemic_root=witness.epistemic_root, authority_root="", valid=witness.valid, wid=wid)


def independent_evidence_count(witnesses: Iterable[Witness]) -> int:
    """|ρ_E| for a set of witnesses, computed via the committed epistemic_roots primitive.
    Two witnesses sharing a root are one witness, not two."""
    reps = [Representation(id=w.wid or f"w{i}", root=w.epistemic_root)
            for i, w in enumerate(witnesses) if w.epistemic_root]
    return n_epi(reps)


# ── swarm non-amplification (TCB-relative): composing zero-authority witnesses yields zero authority ──
def authority_roots(witnesses: Iterable[Witness]) -> FrozenSet[str]:
    """The set of recognised authority roots present. A witness contributes one only if it is
    authority-typed AND carries an authority root; no union of non-authority witnesses can mint one."""
    return frozenset(w.authority_root for w in witnesses
                     if w.authority_root and A in w.warrant_coords)


def swarm_has_authority(witnesses: Iterable[Witness]) -> bool:
    return len(authority_roots(witnesses)) > 0
