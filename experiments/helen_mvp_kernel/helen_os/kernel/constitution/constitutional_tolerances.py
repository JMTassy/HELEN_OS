r"""Constitutional Tolerances — don't just test whether the gate
closes; measure its tolerances.

NON_SOVEREIGN · authority=false · canon=false · ledger_effect=none.

Source, graded honestly: the 1947 Hamilton factory film, RELAYED as
transcript. The harvested engineering laws, made executable against
the real admission predicate (`ceiling_algebra.admit`):

  MICRODEPENDENCY LAW   gate reliability <= reliability of its
                        weakest dependency. Reliability is
                        manufactured below the level at which the
                        user can observe it.

  MARGIN LAW            Admitted != robustly admitted.
                            M(delta) = min(m_P, m_S, m_A)
                        C(delta)=1 is not enough; you want
                        C(delta)=1 and M(delta) >> 0. A delta using
                        its full grant is BARELY admissible: the
                        next unit of drift necessarily lands outside
                        the grant. Slack absorbs drift; the edge
                        converts drift into violation. (REPLAY is
                        binary here — freshness is not yet
                        quantified — so it is named as the least-
                        instrumented dependency rather than
                        pretending it has a margin.)

  SENSITIVITY           the Garden should hunt not only dramatic
                        attacks but sup_{|dx|<=eps} d(F(S+dx),F(S)):
                        the smallest admissible-looking perturbation
                        with the largest constitutional divergence —
                        two ADMITTED deltas one epsilon apart whose
                        effects diverge macroscopically.

  YIELD LAW             quality is produced by REJECTION. Hamilton's
                        hairspring yield: ~1000 lb raw -> ~25 lb
                        usable, ~2.5%. Selectivity << 1 is health,
                        not failure. Do not optimize the Garden for
                        yield; optimize the admitted residue for
                        stability.

  ELINVAR LAW           same constitution under different
                        environments: chi_C = dC/de ~ 0 for
                        constitutionally irrelevant perturbations
                        (naming, ordering, wording), sensitive only
                        to constitutionally relevant evidence.
                        Low-temperature-coefficient governance.

  HAIRSPRING            the oscillator: a fixed reference corpus H of
                        invariant historical cases. D_t = d(E(K_t,H),
                        E(K_0,H)). D_t > 0 without an amendment
                        receipt => HOLD — not because change is
                        forbidden, but because UNRECEIPTED
                        interpretive drift is forbidden. This is the
                        empirical companion to semantic_persistence's
                        pi_K: pi_K guards what the words mean; the
                        oscillator guards what the gate DOES.

Deterministic: no wall-clock, no randomness, canonical serialization.
"""
from __future__ import annotations

import json
import sys
from dataclasses import replace
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import ceiling_algebra as ca

HAMILTON_HAIRSPRING_YIELD = 0.025          # ~1000 lb raw -> ~25 lb usable

# what a unit of effect actually moves, constitutionally
EFFECT_WEIGHTS = {"ledger_root": 100.0, "kernel_glossary": 50.0,
                  "obj_A": 5.0, "obj_B": 5.0, "ui_note": 1.0}

MARGIN_DIMS = ("PROOF", "SCOPE", "AUTHORITY")


def canon(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str)


# ── the Margin Law: M(delta) = min(m_P, m_S, m_A) ───────────────────────

def margins(d: ca.Transition, r: ca.Receipt) -> dict:
    """Distance from each ceiling, for an admitted delta: unused grant
    (PROOF, SCOPE) and grade gap (AUTHORITY). REPLAY is reported as
    UNINSTRUMENTED — binary validity, no quantified freshness — and
    the microdependency law caps the gate's tolerance claim there."""
    v = ca.admit(d, r)
    m = {"PROOF": len(r.proof_ceiling - d.proof_roots),
         "SCOPE": len(r.scope_ceiling - d.effect_objects),
         "AUTHORITY": ca._auth_rank(r.authority_ceiling) -
                      ca._auth_rank(d.authority_needed)}
    big_m = min(m.values()) if v["verdict"] == "ADMIT" else None
    thinnest = min(m, key=lambda k: (m[k], k)) \
        if v["verdict"] == "ADMIT" else None
    return {"verdict": v["verdict"], "margins": m,
            "M": big_m, "thinnest_tolerance": thinnest,
            "replay_axis": "UNINSTRUMENTED — binary; freshness not "
                           "yet quantified; least-instrumented "
                           "dependency of this gate",
            "robustly_admitted": v["verdict"] == "ADMIT" and
                                 big_m is not None and big_m >= 1,
            "barely_admitted": v["verdict"] == "ADMIT" and big_m == 0,
            "law": "Admitted != robustly admitted; C(delta)=1 with "
                   "M(delta)=0 is a gate one drift-unit from breach"}


# ── unit drift: the smallest realistic perturbation per dimension ──────

def drift_one(d: ca.Transition, r: ca.Receipt, dim: str) -> ca.Transition:
    """One epsilon of drift toward the nearest available dependency.
    With slack, the drift lands INSIDE the grant; at the edge, the
    same-size drift necessarily lands outside. Slack absorbs drift."""
    if dim == "PROOF":
        unused = sorted(r.proof_ceiling - d.proof_roots)
        new = unused[0] if unused else "root_PAST_THE_GRANT"
        return replace(d, proof_roots=d.proof_roots | {new})
    if dim == "SCOPE":
        unused = sorted(r.scope_ceiling - d.effect_objects)
        new = unused[0] if unused else "obj_PAST_THE_GRANT"
        return replace(d, effect_objects=d.effect_objects | {new})
    if dim == "AUTHORITY":
        idx = ca._auth_rank(d.authority_needed)
        nxt = ca.AUTHORITY_GRADES[min(idx + 1,
                                      len(ca.AUTHORITY_GRADES) - 1)]
        return replace(d, authority_needed=nxt)
    raise ValueError("E_UNKNOWN_DRIFT_DIMENSION")


def drift_absorption(d: ca.Transition, r: ca.Receipt) -> dict:
    """The margin theorem, executed: a dimension with margin > 0
    absorbs one unit of drift; a dimension at margin 0 converts the
    SAME drift into a ceiling breach."""
    base = margins(d, r)
    out = {}
    for dim in MARGIN_DIMS:
        after = ca.admit(drift_one(d, r, dim), r)
        out[dim] = {"margin": base["margins"][dim],
                    "after_unit_drift": after["verdict"],
                    "absorbed": after["verdict"] == "ADMIT"}
    consistent = all(
        (out[k]["margin"] > 0) == out[k]["absorbed"] for k in out)
    return {"dimensions": out,
            "margin_predicts_absorption": consistent,
            "law": "slack absorbs drift; the edge converts drift "
                   "into violation"}


# ── constitutional sensitivity: admitted, one epsilon apart, far ────────

def effect_divergence(d1: ca.Transition, d2: ca.Transition) -> float:
    sym = d1.effect_objects ^ d2.effect_objects
    return round(sum(EFFECT_WEIGHTS.get(o, 1.0) for o in sym), 6)


def sensitivity_search(d: ca.Transition, r: ca.Receipt) -> dict:
    """The Garden's sup: over all one-object in-scope extensions of an
    ADMITTED delta, which stays ADMITTED yet diverges most? A pair
    C(tau)=C(tau')=1 with d(Effect) >> eps is the dangerous case —
    little things making a vitally big difference."""
    candidates = []
    for obj in sorted(r.scope_ceiling - d.effect_objects):
        d2 = replace(d, effect_objects=d.effect_objects | {obj})
        if ca.admit(d2, r)["verdict"] == "ADMIT":
            candidates.append(
                {"added_object": obj, "epsilon": 1,
                 "divergence": effect_divergence(d, d2)})
    worst = max(candidates, key=lambda c: (c["divergence"],
                                           c["added_object"])) \
        if candidates else None
    return {"admitted_neighbors": candidates,
            "worst_case": worst,
            "sensitivity_found": bool(worst) and
                worst["divergence"] >= 50.0,
            "law": "hunt the smallest admissible-looking perturbation "
                   "with the largest constitutional divergence"}


# ── the Microdependency Law ─────────────────────────────────────────────

def gate_reliability(dependencies: dict, claimed: float) -> dict:
    """A ceiling is only as trustworthy as its smallest dependency —
    hash normalization, timestamp parsing, entity resolution, the
    grade ladder. Claiming above the floor is refused."""
    floor = min(dependencies.values())
    weakest = min(dependencies, key=lambda k: (dependencies[k], k))
    ok = claimed <= floor
    return {"dependency_floor": floor, "weakest": weakest,
            "claimed": claimed, "claim_admissible": ok,
            "reason": None if ok else "E_RELIABILITY_OVERCLAIM",
            "law": "gate reliability <= reliability of its weakest "
                   "dependency; reliability is manufactured below "
                   "the level at which the user can observe it"}


# ── the Yield Law: quality is produced by rejection ─────────────────────

def garden_yield(candidates: tuple, r: ca.Receipt,
                 margin_floor: int = 0) -> dict:
    """Admit with a margin floor. Selectivity may be << 1 — that is
    the cost of the standard, not a defect. The optimization target
    is the STABILITY of the admitted residue (its mean margin), not
    the admission rate."""
    admitted = []
    for d in candidates:
        m = margins(d, r)
        if m["verdict"] == "ADMIT" and m["M"] >= margin_floor:
            admitted.append((d.delta_id, m["M"]))
    n = len(candidates)
    selectivity = round(len(admitted) / n, 6) if n else 0.0
    residue_stability = round(sum(m for _, m in admitted) /
                              len(admitted), 6) if admitted else 0.0
    return {"generated": n, "admitted": len(admitted),
            "selectivity": selectivity,
            "residue_stability": residue_stability,
            "hamilton_hairspring_yield": HAMILTON_HAIRSPRING_YIELD,
            "low_yield_is_pathology": False,
            "law": "do not optimize the Garden for yield; optimize "
                   "the admitted residue for stability"}


# ── the Elinvar Law: chi_C, constitutional susceptibility ───────────────

def chi_susceptibility(d: ca.Transition, r: ca.Receipt) -> dict:
    """Same constitution under different environments. Irrelevant
    perturbations — renaming, re-labeling, set-order — must not move
    the verdict (chi ~ 0); removing a constitutionally relevant piece
    of evidence MUST move it (chi = 1)."""
    base = ca.admit(d, r)["verdict"]
    irrelevant = (
        replace(d, delta_id=d.delta_id + "_renamed"),
        ca.Transition(d.delta_id, frozenset(sorted(d.proof_roots)),
                      frozenset(sorted(d.effect_objects)),
                      d.authority_needed, d.preconditions_replay_valid),
    )
    irr_verdicts = [ca.admit(x, r)["verdict"] for x in irrelevant]
    irr_flips = sum(1 for v in irr_verdicts if v != base)
    # relevant: the receipt loses a root the delta actually rests on
    shrunk = ca.Receipt(r.receipt_id,
                        r.proof_ceiling - frozenset(
                            sorted(d.proof_roots)[:1]),
                        r.scope_ceiling, r.authority_ceiling)
    rel_flip = ca.admit(d, shrunk)["verdict"] != base
    return {"chi_irrelevant": round(irr_flips / len(irrelevant), 6),
            "chi_relevant": 1.0 if rel_flip else 0.0,
            "elinvar": irr_flips == 0 and rel_flip,
            "law": "low-temperature-coefficient governance: invariant "
                   "to naming, ordering and wording; sensitive only "
                   "to constitutionally relevant evidence"}


# ── the Hairspring: the constitutional reference oscillator ─────────────

def reference_corpus() -> tuple:
    """H: invariant historical cases with sealed expected verdicts —
    the fixed rhythm repeated decisions are compared against."""
    r = ca.Receipt("r_ref", frozenset({"root_R"}), frozenset({"obj_A"}),
                   "REPORTED")
    return (
        ("exact_grade_admits",
         ca.Transition("h1", frozenset({"root_R"}), frozenset({"obj_A"}),
                       "REPORTED", True), r, "ADMIT"),
        ("foreign_root_rejects",
         ca.Transition("h2", frozenset({"root_R", "root_X"}),
                       frozenset({"obj_A"}), "REPORTED", True), r,
         "REJECT"),
        ("out_of_scope_rejects",
         ca.Transition("h3", frozenset({"root_R"}),
                       frozenset({"obj_A", "obj_Z"}), "REPORTED", True),
         r, "REJECT"),
        ("over_grade_rejects",
         ca.Transition("h4", frozenset({"root_R"}), frozenset({"obj_A"}),
                       "ADJUDICATED", True), r, "REJECT"),
        ("stale_premise_rejects",
         ca.Transition("h5", frozenset({"root_R"}), frozenset({"obj_A"}),
                       "REPORTED", False), r, "REJECT"),
    )


def oscillator_check(gate_fn, amendment_receipt: str = "") -> dict:
    """D_t = d(E(K_t, H), E(K_0, H)). Disagreement with the sealed
    corpus without an amendment receipt is HOLD — unreceipted
    interpretive drift is forbidden; receipted amendment is lawful."""
    disagreements = []
    for name, d, r, expected in reference_corpus():
        got = gate_fn(d, r)["verdict"]
        if got != expected:
            disagreements.append({"case": name, "expected": expected,
                                  "got": got})
    d_t = len(disagreements)
    if d_t == 0:
        verdict = "REFERENCE_HELD"
    elif amendment_receipt:
        verdict = "AMENDED_UNDER_RECEIPT"
    else:
        verdict = "HOLD"
    return {"D_t": d_t, "disagreements": disagreements,
            "verdict": verdict,
            "reason": "E_INTERPRETIVE_DRIFT" if verdict == "HOLD"
                      else None,
            "law": "change is not forbidden; UNRECEIPTED interpretive "
                   "drift is"}


def lenient_gate(d: ca.Transition, r: ca.Receipt) -> dict:
    """A drifted interpretation for the oscillator to catch: reads
    'one grade over' as close enough. Every decision it makes looks
    locally reasonable; the reference corpus exposes it."""
    if ca._auth_rank(d.authority_needed) == \
            ca._auth_rank(r.authority_ceiling) + 1:
        eased = ca.Receipt(r.receipt_id, r.proof_ceiling,
                           r.scope_ceiling, d.authority_needed)
        return ca.admit(d, eased)
    return ca.admit(d, r)
