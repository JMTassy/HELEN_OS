r"""Four-Ceiling Minimality — remove each ceiling, watch an invalid
delta walk in.

NON_SOVEREIGN · authority=false · canon=false · ledger_effect=none.

The operator's target, verbatim:

    Minimality would require something stronger: remove each primitive
    in turn and construct a counterexample that becomes admissible.
    For ceilings C_i:

        forall C_i, exists delta_i :
            not C_i(delta_i)
            /\  AND_{j != i} C_j(delta_i)
            /\  Invalid(delta_i)

This module produces the four witnesses executably, against the REAL
admission predicate (`ceiling_algebra.admit`), and runs the ablation:
`admit_without(delta, r, C_i)` is the gate with ceiling C_i removed.
For each ceiling there is a delta that

    1. breaches EXACTLY that ceiling (the other three hold),
    2. is Invalid — it enacts a named harm class, each one witnessed
       in this project's own history, and
    3. is ADMITTED by the ablated gate, while every OTHER ablation
       still rejects it.

Point 3 is the irreducibility content: dropping C_i admits delta_i and
nothing else catches it, so no proper subset of {P,S,A,R} rejects all
four witnesses. Each ceiling is individually load-bearing.

On Invalid(delta): invalidity is grounded by construction in the
tested domain — each witness enacts a harm the constitution names
(fabricated evidence root; out-of-grant mutation; self-granted
authority; effect on a premise that no longer replays). There is no
external invalidity oracle; that boundedness is stated, not hidden.

Combined with the compositional-closure result (all four ceilings
break under naive per-op evaluation, all four attacks are caught by
transactional evaluation of the SAME four, no fifth earned), the
verdict this module is allowed to state is exactly:

    the four-ceiling basis is IRREDUCIBLE and COMPOSITIONALLY
    ADEQUATE over the tested domain.

Evidence, never proof. Completeness stays UNKNOWN.

What survives the reduction (the three preserved primitives):
    1. four-ceiling admission        Admit = P /\ S /\ A /\ R
    2. generation/admission split    G(x) does not entail A(x)
    3. witness supremacy             report does not entail state
       (possibly derivable from REPLAY+PROOF — open, recorded)

Deterministic: no wall-clock, no randomness, canonical serialization.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import ceiling_algebra as ca
import compositional_closure as ccl

CEILINGS = ("PROOF", "SCOPE", "AUTHORITY", "REPLAY")

PRESERVED_PRIMITIVES = (
    "four-ceiling admission: Admit = PROOF /\\ SCOPE /\\ AUTHORITY "
    "/\\ REPLAY",
    "generation/admission separation: Generate(x) does not entail "
    "Admit(x)",
    "witness supremacy: report does not entail state (possibly "
    "derivable from REPLAY+PROOF; open question, recorded not "
    "resolved)",
)


def canon(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str)


# ── the ablated gate: the same predicate with one conjunct removed ──────

def admit_without(delta: ca.Transition, r: ca.Receipt,
                  dropped: str) -> dict:
    """Admit_{-i}: evaluate `ceiling_algebra.admit` and discard the
    breaches of the dropped ceiling. This IS removing the conjunct —
    the other three are evaluated by the real gate, untouched."""
    if dropped not in CEILINGS:
        raise ValueError("E_UNKNOWN_CEILING")
    full = ca.admit(delta, r)
    remaining = [b for b in full.get("breaches", ())
                 if b["ceiling"] != dropped]
    return {"dropped_ceiling": dropped,
            "verdict": "REJECT" if remaining else "ADMIT",
            "breaches": remaining,
            "full_gate_verdict": full["verdict"]}


# ── the four witnesses: each fails exactly one ceiling, and is Invalid ──
# One shared receipt; each delta exceeds it in exactly one dimension.

RECEIPT = ca.Receipt(
    receipt_id="r_minimality",
    proof_ceiling=frozenset({"root_R"}),
    scope_ceiling=frozenset({"obj_A"}),
    authority_ceiling="REPORTED",
)


def _witness(target: str, delta: ca.Transition, harm: str,
             harm_witnessed_as: str) -> dict:
    return {"target_ceiling": target, "delta": delta,
            "invalid_because": harm,
            "harm_class_witnessed_in_project_history": harm_witnessed_as}


def witness_proof() -> dict:
    """delta_PROOF rests on an evidence root the receipt never granted
    — a manufactured witness. Scope, authority, replay all clean."""
    return _witness(
        "PROOF",
        ca.Transition("d_proof_only",
                      proof_roots=frozenset({"root_R", "root_FORGED"}),
                      effect_objects=frozenset({"obj_A"}),
                      authority_needed="REPORTED",
                      preconditions_replay_valid=True),
        "claims an evidence root outside the granted proof ceiling — "
        "evidence manufactured, not witnessed",
        "derived-of-derived witness inflation; RELAY promoted to "
        "DIRECTLY_OBSERVED")


def witness_scope() -> dict:
    """delta_SCOPE mutates an object outside the grant. Proof,
    authority, replay all clean."""
    return _witness(
        "SCOPE",
        ca.Transition("d_scope_only",
                      proof_roots=frozenset({"root_R"}),
                      effect_objects=frozenset({"obj_A", "obj_FOREIGN"}),
                      authority_needed="REPORTED",
                      preconditions_replay_valid=True),
        "mutates an object no receipt placed in scope",
        "the helen_kernel/ deploy outside the authorized surface — "
        "caught by the operator, relocated forward-only")


def witness_authority() -> dict:
    """delta_AUTHORITY performs an admission-grade act on a
    report-grade grant. Proof, scope, replay all clean."""
    return _witness(
        "AUTHORITY",
        ca.Transition("d_authority_only",
                      proof_roots=frozenset({"root_R"}),
                      effect_objects=frozenset({"obj_A"}),
                      authority_needed="ADMITTED",
                      preconditions_replay_valid=True),
        "acts at an authority grade above the grant — authority "
        "self-granted",
        "council recommends, never admits; only player admission "
        "mutates the world")


def witness_replay() -> dict:
    """delta_REPLAY takes effect on preconditions that no longer
    reconstruct from committed history. Proof, scope, authority all
    clean."""
    return _witness(
        "REPLAY",
        ca.Transition("d_replay_only",
                      proof_roots=frozenset({"root_R"}),
                      effect_objects=frozenset({"obj_A"}),
                      authority_needed="REPORTED",
                      preconditions_replay_valid=False),
        "effect rests on a premise that does not replay from committed "
        "history",
        "ghost commits 3e0e2b4 / fff21ef — hashes that resolve on no "
        "branch are not commits")


def minimality_witnesses() -> tuple:
    return (witness_proof(), witness_scope(), witness_authority(),
            witness_replay())


# ── checking a witness: the three-conjunct condition, executably ────────

def check_witness(w: dict) -> dict:
    r"""Verify not C_i(delta_i) /\ AND_{j!=i} C_j(delta_i) /\
    Invalid(delta_i) — and the irreducibility payload: the ablation of
    C_i ADMITS delta_i while every other ablation still rejects it."""
    target, delta = w["target_ceiling"], w["delta"]
    full = ca.admit(delta, RECEIPT)
    breached = sorted({b["ceiling"] for b in full.get("breaches", ())})

    violates_only_target = breached == [target]
    others_hold = all(c not in breached for c in CEILINGS if c != target)
    # Invalid, operationalized: the full gate rejects it AND the delta
    # enacts a named harm class (grounded in the tested domain).
    invalid = full["verdict"] == "REJECT" and bool(w["invalid_because"])

    ablations = {c: admit_without(delta, RECEIPT, c)["verdict"]
                 for c in CEILINGS}
    admitted_when_target_dropped = ablations[target] == "ADMIT"
    rejected_under_other_ablations = all(
        v == "REJECT" for c, v in ablations.items() if c != target)

    return {"target_ceiling": target,
            "delta_id": delta.delta_id,
            "violates_only_target": violates_only_target,
            "others_hold": others_hold,
            "invalid": invalid,
            "invalid_because": w["invalid_because"],
            "ablation_verdicts": ablations,
            "admitted_when_target_dropped": admitted_when_target_dropped,
            "rejected_under_other_ablations":
                rejected_under_other_ablations,
            "witness_holds": (violates_only_target and others_hold and
                              invalid and admitted_when_target_dropped)}


def irreducibility() -> dict:
    """The four witnesses, checked. If each ablation admits its invalid
    witness, no proper subset of the basis rejects all four — every
    ceiling is individually load-bearing."""
    checks = tuple(check_witness(w) for w in minimality_witnesses())
    all_hold = all(c["witness_holds"] for c in checks)
    covered = sorted(c["target_ceiling"] for c in checks)
    return {"claim": "forall C_i exists delta_i: not C_i(delta_i) /\\ "
                     "AND_{j!=i} C_j(delta_i) /\\ Invalid(delta_i)",
            "witnesses": checks,
            "ceilings_witnessed": covered,
            "every_ceiling_witnessed": covered == sorted(CEILINGS),
            "each_ablation_admits_its_invalid_witness": all_hold,
            "irreducible_over_tested_domain": all_hold and
                covered == sorted(CEILINGS),
            "grade": "EVIDENCE_NOT_PROOF",
            "law": "dropping any one ceiling admits a constitutionally "
                   "invalid transition that no remaining ceiling "
                   "catches; each ceiling is individually load-bearing"}


# ── the compositional-closure attack, re-run against this verdict ───────

def run_compositional_attack() -> dict:
    """The four composed counterexamples from compositional_closure,
    executed: each locally admissible, each globally violating, each
    caught by transactional evaluation of the same four ceilings."""
    CLEAN = {c: True for c in CEILINGS}
    cases = (
        ("SCOPE",
         (ccl.Delta("d1", CLEAN, flow_from="X", writes=frozenset({"b1"})),
          ccl.Delta("d2", CLEAN, flow_from="b1", flow_to="Z",
                    writes=frozenset({"Z"}))),
         {"forbidden_flows": {("X", "Z")}}),
        ("AUTHORITY",
         (ccl.Delta("d1", CLEAN, ontology_delta=-1),
          ccl.Delta("d2", CLEAN,
                    asserts_identity="hull_B:nationality=Dutch")),
         {"authorized_identities": ()}),
        ("PROOF",
         (ccl.Delta("d1", CLEAN, produces_artifact="a", evidence_root="R"),
          ccl.Delta("d2", CLEAN, produces_artifact="b", derives_from="a"),
          ccl.Delta("d3", CLEAN, produces_artifact="c", derives_from="b")),
         {"claimed_independent_roots": 3}),
        ("REPLAY",
         (ccl.Delta("d1", CLEAN, premise_root="R", t=0),
          ccl.Delta("d2", CLEAN, premise_root="R", t=2)),
         {"revoked_at": {"R": 2}}),
    )
    results = []
    for expected, trace, inv in cases:
        gap = ccl.compositional_gap(trace, inv)
        results.append({"ceiling": expected,
                        "compositional_gap": gap["compositional_gap"],
                        "caught_transactionally":
                            gap["breached_ceilings"] == [expected],
                        "needs_fifth_ceiling":
                            gap["needs_fifth_ceiling"]})
    survived = all(r["compositional_gap"] and r["caught_transactionally"]
                   and r["needs_fifth_ceiling"] is False for r in results)
    return {"attacks": results, "survived": survived,
            "fifth_ceiling_earned": False if survived else None}


# ── the combined verdict — stated no stronger than earned ───────────────

def basis_verdict() -> dict:
    """Irreducibility witnesses + compositional-closure survival. The
    strongest sentence this evidence licenses, and no stronger."""
    irr = irreducibility()
    comp = run_compositional_attack()
    both = irr["irreducible_over_tested_domain"] and comp["survived"]
    return {"irreducible_over_tested_domain":
                irr["irreducible_over_tested_domain"],
            "compositionally_adequate_over_tested_domain":
                comp["survived"],
            "verdict": ("FOUR_CEILING_BASIS_IRREDUCIBLE_AND_"
                        "COMPOSITIONALLY_ADEQUATE_OVER_TESTED_DOMAIN"
                        if both else "NOT_ESTABLISHED"),
            "preserved_primitives": PRESERVED_PRIMITIVES,
            "grade": "EVIDENCE_NOT_PROOF",
            "completeness": "UNKNOWN",
            "domain_bound": "the tested domain only; NotObserved(a "
                            "fifth-ceiling counterexample) does not "
                            "entail Impossible",
            "open_question": "can four-ceiling admission + generation/"
                             "admission separation, with witness "
                             "semantics, generate all required "
                             "governance behavior?"}
