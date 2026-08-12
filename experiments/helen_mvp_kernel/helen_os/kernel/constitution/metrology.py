r"""Metrology — the architecture locked: CONSTITUTION -> INSTRUMENT
-> METROLOGY, with Garden as adversarial calibration.

NON_SOVEREIGN · authority=false · canon=false · ledger_effect=none.

The operator's lock ruling, with one mathematical correction applied
before treating the margin as specification: the margin is SIGNED.

    mu_C(tau) = +d_C(tau, boundary)   if tau admissible
                -d_C(tau, boundary)   if tau not admissible

The dangerous regime is mu_C -> 0 FROM THE FAIL SIDE. Garden's
calibration objective:

    alpha_-(m) = Pr[ V(tau)=PASS | C*(tau)=FAIL, -mu_C(tau)=m ]

attacked at m -> 0 while maximizing alpha_-. That is a calibration
experiment, not ordinary adversarial testing: the verifier's failure
surface lives AT the boundary, and sampling far from it learns
nothing.

The frozen stack:

    C = (P, S, A, R)          CONSTITUTION
    I = (V, W, Pi)            INSTRUMENT  (verifier, witness
                                          generator, replayer)
    M(I)                      METROLOGY   (calibration of the
                                          instrument, not merely of
                                          the classifier bit)

Deliberately M(I), not M(V): a PASS that cannot be reconstructed is
epistemically different from a PASS with a deterministic witness and
successful independent replay. Hence the traceability split:

    chi_W  = Pr[ valid witness emitted ]
    chi_Pi = Pr[ independent replay reproduces verdict | W valid ]

one aggregate number may not conceal which stage failed.

Portable evidence: every reported scalar is really the tuple
(estimate, uncertainty, population, environment, adversary,
procedure, version). Without those coordinates the number is not
portable evidence — it is refused as such.

Anti-gaming law:  N_tests UP  does not imply  confidence UP.
100,000 near-duplicates far from the boundary enlarge the suite while
learning almost nothing. The scarce resource is independent
adversarial information near the failure frontier. Garden's identity,
cleaned: ADAPTIVE EXPERIMENTAL DESIGN FOR HELEN'S VERIFICATION
INSTRUMENT — choose the next trace because its adjudicated outcome
maximally reduces uncertainty about the verifier's failure surface.

The resolution law, bounded (no omniscient verification demanded):

    for all e in E_critical:   R_I(e) < R_required(e)

Never let CONSTITUTIONALLY RELEVANT system behavior outrun the
calibrated resolution of its falsification instrument. Resolution is
owed over the constitutionally relevant failure manifold, not
globally.

Escalation rule for a Garden-discovered failure:
    C inadequate     -> constitutional revision candidate
    V misclassifies  -> instrument repair
    W insufficient   -> witness repair
    Pi fails         -> replay repair
    M cannot resolve -> METROLOGY UPGRADE      (the Hamilton branch)

And the guardrail that matters most: a metrology failure does NOT
authorize a fifth ceiling.

    UNKNOWN RESOLUTION  is not  NEW LAW.

Uncertainty about our ability to verify the constitution must not
silently mutate the constitution itself.

Historical premise, bounded as relayed: Hamilton's Model 21 reported
within ~0.5 s/day against a Navy spec of 1.55 s/day, and the Time
Comparator (dial error to 1/100 s/day) was built after existing
observatory procedure proved insufficient — a metrology upgrade, not
a new law of timekeeping.

Deterministic: no wall-clock, no randomness, canonical serialization.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import ceiling_algebra as ca
import constitutional_tolerances as ct

ARCHITECTURE_FROZEN = ("CONSTITUTION (P,S,A,R)",
                       "INSTRUMENT (V,W,Pi)",
                       "METROLOGY M(I)")

GARDEN_IDENTITY = ("adaptive experimental design for HELEN's "
                   "verification instrument")

# relayed Hamilton metrology facts (grade REPORTED)
MODEL_21_SEC_PER_DAY = 0.5
NAVY_SPEC_SEC_PER_DAY = 1.55
TIME_COMPARATOR_RESOLUTION = 0.01

EVIDENCE_COORDS = ("estimate", "uncertainty", "population",
                   "environment", "adversary", "procedure", "version")

ESCALATION_ROUTES = {
    "C_INADEQUATE": "constitutional_revision_candidate",
    "V_MISCLASSIFIES": "instrument_repair",
    "W_INSUFFICIENT": "witness_repair",
    "PI_FAILS": "replay_repair",
    "M_CANNOT_RESOLVE": "metrology_upgrade",
}


def canon(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str)


# ── the correction: the SIGNED constitutional margin ────────────────────

def signed_margin(d: ca.Transition, r: ca.Receipt) -> dict:
    """mu_C: positive distance-to-boundary inside the admissible set,
    negative outside (minimal unit edits to reach admissibility)."""
    v = ca.admit(d, r)
    if v["verdict"] == "ADMIT":
        mu = ct.margins(d, r)["M"]
        return {"mu": mu, "side": "PASS",
                "law": "the dangerous regime is mu -> 0 from the "
                       "FAIL side"}
    dist = (len(d.proof_roots - r.proof_ceiling) +
            len(d.effect_objects - r.scope_ceiling) +
            max(0, ca._auth_rank(d.authority_needed) -
                ca._auth_rank(r.authority_ceiling)) +
            (0 if d.preconditions_replay_valid else 1))
    return {"mu": -dist, "side": "FAIL",
            "law": "the dangerous regime is mu -> 0 from the "
                   "FAIL side"}


# ── a defective verifier for calibration: the microdependency bites ────

def sloppy_verifier(d: ca.Transition, r: ca.Receipt) -> dict:
    """V with a case-normalization defect in its PROOF check — exactly
    the hash-normalization microdependency named in gate_reliability.
    Far from the boundary it agrees with C*; AT the boundary (a root
    foreign only by case) it falsely admits."""
    roots = {x.lower() for x in d.proof_roots}
    ceil = {x.lower() for x in r.proof_ceiling}
    if roots <= ceil:
        healed = ca.Transition(d.delta_id,
                               frozenset(x for x in r.proof_ceiling
                                         if x.lower() in roots),
                               d.effect_objects, d.authority_needed,
                               d.preconditions_replay_valid)
        return ca.admit(healed, r)
    return ca.admit(d, r)


def alpha_minus(verifier, cases: tuple, r: ca.Receipt) -> dict:
    """alpha_-(m): among ground-truth-FAIL cases at distance m from
    the boundary, the rate at which V falsely says PASS."""
    by_m = {}
    for d in cases:
        truth = ca.admit(d, r)["verdict"]
        if truth != "REJECT":
            continue
        m = -signed_margin(d, r)["mu"]
        got = verifier(d, r)["verdict"]
        bucket = by_m.setdefault(m, {"n": 0, "false_pass": 0})
        bucket["n"] += 1
        bucket["false_pass"] += 1 if got == "ADMIT" else 0
    return {m: {"n": b["n"],
                "alpha_minus": round(b["false_pass"] / b["n"], 6)}
            for m, b in sorted(by_m.items())}


# ── the instrument I = (V, W, Pi) and the chi split ─────────────────────

WITNESS_FIELDS = ("delta_id", "proof_roots", "effect_objects",
                  "authority_needed", "replay_valid", "receipt_id",
                  "proof_ceiling", "scope_ceiling", "authority_ceiling",
                  "verdict")


def make_witness(verifier, d: ca.Transition, r: ca.Receipt) -> dict:
    """W: everything an independent party needs to reproduce the
    verdict from scratch."""
    return {"delta_id": d.delta_id,
            "proof_roots": sorted(d.proof_roots),
            "effect_objects": sorted(d.effect_objects),
            "authority_needed": d.authority_needed,
            "replay_valid": d.preconditions_replay_valid,
            "receipt_id": r.receipt_id,
            "proof_ceiling": sorted(r.proof_ceiling),
            "scope_ceiling": sorted(r.scope_ceiling),
            "authority_ceiling": r.authority_ceiling,
            "verdict": verifier(d, r)["verdict"]}


def witness_is_valid(w: dict) -> bool:
    return all(f in w for f in WITNESS_FIELDS)


def replay_witness(w: dict) -> dict:
    """Pi: independent reconstruction — rebuild delta and receipt from
    the witness alone, re-adjudicate with the REAL gate, compare."""
    if not witness_is_valid(w):
        return {"replayed": False, "reproduces": False,
                "reason": "E_WITNESS_INSUFFICIENT",
                "missing": sorted(set(WITNESS_FIELDS) - set(w))}
    d = ca.Transition(w["delta_id"], frozenset(w["proof_roots"]),
                      frozenset(w["effect_objects"]),
                      w["authority_needed"], w["replay_valid"])
    r = ca.Receipt(w["receipt_id"], frozenset(w["proof_ceiling"]),
                   frozenset(w["scope_ceiling"]),
                   w["authority_ceiling"])
    got = ca.admit(d, r)["verdict"]
    return {"replayed": True, "reproduces": got == w["verdict"],
            "independent_verdict": got, "witnessed_verdict": w["verdict"]}


def chi_split(witness_maker, verifier, cases: tuple,
              r: ca.Receipt) -> dict:
    """chi_W and chi_Pi, separately — one aggregate may not conceal
    which stage failed. A PASS that cannot be reconstructed is
    epistemically different from a PASS with a deterministic witness
    and successful independent replay."""
    n = len(cases)
    witnesses = [witness_maker(verifier, d, r) for d in cases]
    valid = [w for w in witnesses if witness_is_valid(w)]
    reproduced = [w for w in valid if replay_witness(w)["reproduces"]]
    return {"chi_W": round(len(valid) / n, 6) if n else 0.0,
            "chi_Pi": round(len(reproduced) / len(valid), 6)
                      if valid else 0.0,
            "law": "M(I), not M(V): the classifier bit being right "
                   "does not make the pass reconstructible"}


def broken_witness_maker(verifier, d: ca.Transition,
                         r: ca.Receipt) -> dict:
    """A W defect: correct verdict bit, receipt half omitted. The
    metrology must see this even though V is perfect."""
    w = make_witness(verifier, d, r)
    for f in ("receipt_id", "proof_ceiling", "scope_ceiling",
              "authority_ceiling"):
        w.pop(f)
    return w


# ── portable evidence: the seven-coordinate tuple ───────────────────────

def report_scalar(**coords) -> dict:
    """Every reported number carries (estimate, uncertainty,
    population, environment, adversary, procedure, version). A bare
    scalar is refused as evidence."""
    missing = sorted(c for c in EVIDENCE_COORDS if c not in coords)
    if missing:
        return {"portable": False, "reason": "E_UNPORTABLE_EVIDENCE",
                "missing": missing,
                "law": "without its coordinates the number is not "
                       "portable evidence"}
    return {"portable": True,
            "tuple": {c: coords[c] for c in EVIDENCE_COORDS}}


# ── the anti-gaming law: N up does not imply confidence up ──────────────

def frontier_information(cases: tuple, r: ca.Receipt,
                         window: int = 1) -> dict:
    """Independent adversarial information near the failure frontier:
    DISTINCT ground-truth-FAIL cases within `window` of the boundary.
    Duplicates and far-field cases contribute nothing."""
    seen = set()
    for d in cases:
        sm = signed_margin(d, r)
        if sm["side"] == "FAIL" and -sm["mu"] <= window:
            seen.add(canon({"p": sorted(d.proof_roots),
                            "e": sorted(d.effect_objects),
                            "a": d.authority_needed,
                            "r": d.preconditions_replay_valid}))
    return {"n_cases": len(cases),
            "frontier_information": len(seen),
            "law": "N_tests up does not imply epistemic confidence "
                   "up; the scarce resource is independent "
                   "adversarial information near the failure "
                   "frontier"}


# ── the resolution law, bounded to the critical manifold ────────────────

def resolution_check(envs: dict) -> dict:
    """for all e in E_critical: R_I(e) < R_required(e). No omniscient
    verification demanded — a non-critical environment with poor
    resolution does not fail the law."""
    failures = sorted(e for e, v in envs.items()
                      if v.get("critical") and not
                      v["R_I"] < v["R_required"])
    return {"holds": not failures,
            "failing_envs": failures,
            "omniscience_required": False,
            "doctrine": "never let the governed system outrun the "
                        "resolution of its falsifier",
            "precise_law": "never let constitutionally relevant "
                           "system behavior outrun the calibrated "
                           "resolution of its falsification "
                           "instrument"}


# ── the escalation rule, and the guardrail ──────────────────────────────

def escalate(finding_kind: str) -> dict:
    if finding_kind not in ESCALATION_ROUTES:
        return {"route": None, "reason": "E_UNKNOWN_FINDING_KIND"}
    route = ESCALATION_ROUTES[finding_kind]
    return {"finding": finding_kind, "route": route,
            "hamilton_branch": finding_kind == "M_CANNOT_RESOLVE",
            "authorizes_new_law": False,
            "guardrail": "UNKNOWN RESOLUTION is not NEW LAW"}


def mint_law_from_unresolved(observation: str) -> dict:
    """The refused move: metrology says 'cannot resolve', someone
    reaches for a fifth ceiling. Refused by name."""
    return {"observation": observation, "minted": False,
            "reason": "E_UNKNOWN_RESOLUTION_IS_NOT_NEW_LAW",
            "route_instead": "metrology_upgrade",
            "law": "uncertainty about our ability to verify the "
                   "constitution must not silently mutate the "
                   "constitution itself"}
