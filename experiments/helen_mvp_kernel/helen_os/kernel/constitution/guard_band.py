r"""Guard Band — when resolution falls below the decision margin,
authority must contract.

NON_SOVEREIGN · authority=false · canon=false · ledger_effect=none.

The operator's ruling, made executable:

1. THE ADMISSION MEASUREMENT. PASS is not the epistemic object. The
   primitive is

       M(tau) = (y, u, W, Gamma, e, v)

   verdict, calibrated uncertainty, witness, provenance/calibration
   graph, environment, versions. PASS without (u, Gamma, e, v) is an
   INDICATION, not a calibrated result.

2. PER-CEILING SIGNED MARGINS. Binary predicates throw away
   information:

       mu_P, mu_S, mu_A, mu_R    signed;
       mu_C = min(mu_P, mu_S, mu_A, mu_R)

   and the argmin names the ACTIVE CONSTRAINT — every failure has a
   mechanically identifiable bottleneck, no narrative diagnosis.
   (mu_R stays coarse {-1, +1}: the REPLAY axis is still the least-
   instrumented dependency, and it is named, not faked.)

3. THE GUARD BAND. Do not admit merely because mu_hat >= 0. With
   instrument uncertainty u and coverage factor k:

       mu_hat - k*u > 0    =>  ADMIT
       mu_hat + k*u < 0    =>  REJECT
       |mu_hat| <= k*u     =>  HOLD / UNKNOWN

   UNKNOWN is not an exception state. It is the epistemically correct
   output of a finite-resolution constitutional instrument near its
   decision boundary. Instrument uncertainty widens the HOLD region;
   it NEVER weakens the constitution.

4. CALIBRATED ADMISSION:

       ADMIT(tau)  iff  mu_hat - k*u > 0
                        and Gamma valid
                        and Pi reproduces the verdict.

   The Four Ceilings still define constitutionality; everything else
   specifies how confidently we know they passed.

5. THE CHAIN THAT NEVER COLLAPSES:

       Replayable  =/=>  Resolvable  =/=>  Safe to admit.

   No admission decision is stronger than its uncertainty budget and
   traceability chain.

The locked rule — not a fifth ceiling, a guard band around epistemic
authority:

    WHEN RESOLUTION FALLS BELOW THE DECISION MARGIN,
    AUTHORITY MUST CONTRACT.

Deterministic: no wall-clock, no randomness, canonical serialization.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import ceiling_algebra as ca
import metrology as mt

DEFAULT_K = 2.0            # coverage factor

MEASUREMENT_FIELDS = ("y", "u", "W", "Gamma", "e", "v")


def canon(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str)


# ── per-ceiling signed margins, and the active constraint ───────────────

def ceiling_margins_signed(d: ca.Transition, r: ca.Receipt) -> dict:
    """mu_P, mu_S, mu_A, mu_R — positive slack inside each ceiling,
    negative overrun outside it. mu_C = min; argmin = the bottleneck."""
    mu_p = len(r.proof_ceiling - d.proof_roots) \
        if d.proof_roots <= r.proof_ceiling \
        else -len(d.proof_roots - r.proof_ceiling)
    mu_s = len(r.scope_ceiling - d.effect_objects) \
        if d.effect_objects <= r.scope_ceiling \
        else -len(d.effect_objects - r.scope_ceiling)
    mu_a = ca._auth_rank(r.authority_ceiling) - \
        ca._auth_rank(d.authority_needed)
    mu_r = 1 if d.preconditions_replay_valid else -1
    mus = {"PROOF": mu_p, "SCOPE": mu_s, "AUTHORITY": mu_a,
           "REPLAY": mu_r}
    active = min(mus, key=lambda c: (mus[c], c))
    return {"mu": mus, "mu_C": min(mus.values()),
            "active_constraint": active,
            "replay_note": "mu_R is coarse {-1,+1}: the least-"
                           "instrumented dependency, named not faked",
            "law": "every failure has a mechanically identifiable "
                   "bottleneck; no narrative diagnosis required"}


# ── the guard band: three regions, HOLD is epistemically correct ───────

def guarded_decision(mu_hat: float, u: float,
                     k: float = DEFAULT_K) -> dict:
    if u < 0:
        raise ValueError("E_NEGATIVE_UNCERTAINTY")
    if mu_hat - k * u > 0:
        region = "ADMIT"
    elif mu_hat + k * u < 0:
        region = "REJECT"
    else:
        region = "HOLD_UNKNOWN"
    return {"mu_hat": mu_hat, "u": u, "k": k,
            "region": region,
            "hold_width": round(2 * k * u, 6),
            "reason": "E_BELOW_RESOLUTION" if region == "HOLD_UNKNOWN"
                      else None,
            "law": "instrument uncertainty widens the HOLD region; "
                   "it never weakens the constitution"}


# ── the admission measurement: indication vs calibrated result ─────────

def admission_measurement(d: ca.Transition, r: ca.Receipt, u: float,
                          e: str, v: str) -> dict:
    """M(tau) = (y, u, W, Gamma, e, v)."""
    w = mt.make_witness(ca.admit, d, r)
    gamma = {"witness": w,
             "calibration_chain": ("ceiling_algebra.admit",
                                   "metrology.make_witness",
                                   "metrology.replay_witness")}
    return {"y": w["verdict"], "u": u, "W": w, "Gamma": gamma,
            "e": e, "v": v}


def is_calibrated_result(m: dict) -> dict:
    """PASS without (u, Gamma, e, v) is an indication, not a
    calibrated result."""
    missing = sorted(f for f in MEASUREMENT_FIELDS if f not in m
                     or m[f] in (None, ""))
    if missing:
        return {"status": "INDICATION",
                "reason": "E_UNCALIBRATED_PASS",
                "missing": missing,
                "law": "PASS without (u, Gamma, e, v) is an "
                       "indication, not a calibrated result"}
    return {"status": "CALIBRATED_RESULT", "missing": []}


# ── calibrated admission: guard band AND Gamma AND Pi ──────────────────

def calibrated_admit(d: ca.Transition, r: ca.Receipt, u: float,
                     k: float = DEFAULT_K) -> dict:
    """ADMIT(tau) iff mu_hat - k*u > 0 and Gamma valid and Pi
    reproduces. The stronger predicate the operator locked."""
    mu = ceiling_margins_signed(d, r)
    band = guarded_decision(mu["mu_C"], u, k)
    w = mt.make_witness(ca.admit, d, r)
    gamma_valid = mt.witness_is_valid(w)
    pi = mt.replay_witness(w)
    admitted = (band["region"] == "ADMIT" and gamma_valid and
                pi.get("reproduces") is True)
    if admitted:
        verdict = "ADMIT"
    elif band["region"] == "HOLD_UNKNOWN":
        verdict = "HOLD_UNKNOWN"
    else:
        verdict = "REJECT"
    return {"verdict": verdict,
            "mu_C": mu["mu_C"], "active_constraint":
                mu["active_constraint"],
            "band_region": band["region"],
            "gamma_valid": gamma_valid,
            "pi_reproduces": pi.get("reproduces", False),
            "predicate": "mu_hat - k*u > 0 AND Gamma valid AND Pi "
                         "reproduced",
            "note": "the Four Ceilings still define constitutionality; "
                    "everything else specifies how confidently we know "
                    "they passed"}


# ── Replayable =/=> Resolvable =/=> Safe ────────────────────────────────

def epistemic_chain(mu_hat: float, u: float, replay_ok: bool,
                    k: float = DEFAULT_K) -> dict:
    """The three links, separately witnessed — no link entails the
    next."""
    resolvable = abs(mu_hat) > k * u
    safe = replay_ok and resolvable and (mu_hat - k * u > 0)
    return {"replayable": replay_ok,
            "resolvable": resolvable,
            "safe_to_admit": safe,
            "law": "Replayable does not entail Resolvable does not "
                   "entail Safe to admit; no admission decision is "
                   "stronger than its uncertainty budget and "
                   "traceability chain"}


# ── the locked rule ─────────────────────────────────────────────────────

def authority_contraction(mu_hat: float, u: float,
                          k: float = DEFAULT_K) -> dict:
    """WHEN RESOLUTION FALLS BELOW THE DECISION MARGIN, AUTHORITY MUST
    CONTRACT. Not a fifth ceiling; a guard band around epistemic
    authority. The contraction routes to metrology upgrade, never to
    new law."""
    contracts = not (abs(mu_hat) > k * u)
    return {"mu_hat": mu_hat, "resolution": round(k * u, 6),
            "authority_contracts": contracts,
            "verdict_when_contracted": "HOLD_UNKNOWN",
            "is_fifth_ceiling": False,
            "is_guard_band": True,
            "route_on_persistent_contraction":
                mt.ESCALATION_ROUTES["M_CANNOT_RESOLVE"],
            "law": "WHEN RESOLUTION FALLS BELOW THE DECISION MARGIN, "
                   "AUTHORITY MUST CONTRACT"}
