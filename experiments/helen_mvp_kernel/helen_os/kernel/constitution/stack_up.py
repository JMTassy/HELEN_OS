r"""Stack-Up — compositional uncertainty and common ancestry: the two
chiddushes the operator ranked first.

NON_SOVEREIGN · authority=false · canon=false · ledger_effect=none.

1. TOLERANCE STACK-UP (compositional uncertainty). Individually
   conforming dimensions can accumulate into an out-of-spec assembly.
   For a transformation chain x_0 -> x_1 -> ... -> x_n with local
   distortions eps_i = d(x_i, T_i(x_{i-1})):

       (forall i: eps_i <= b_i)  does NOT imply  B(tau) <= B_max

   where B(tau) = d(x_0, x_n) is the trace budget. The Garden target:

       forall i: eps_i <= b_i   AND   B(tau) > B_max

   — constructed here on the canonical pipeline
   source -> summary -> memory -> retrieval -> synthesis -> decision.
   Per-transition P/S/A/R tests simply do not see this failure.

   Margin propagation: mu_C(tau) = Phi(mu_C(delta_i); D_i) where D_i
   is composition distortion. The Phi used here is a MODEL
   (min margin minus accumulated distortion) — its calibration is
   pending; the executable point is only that local positivity does
   not survive composition unmeasured.

2. COMMON ANCESTRY (consensus is not independence). Witness count is
   never evidence strength: |W| = 5 can mean N_independent = 1. The
   measurable primitive comes FIRST — shared ancestry:

       kappa(W_i, W_j) = |Anc_i ∩ Anc_j| / |Anc_i ∪ Anc_j|

   (N_effective is deliberately NOT defined yet; independence is
   subtle, and minting a number before the primitive is measured
   would be manufactured precision.) The Garden attack: maximize
   apparent consensus while minimizing independent ancestry —
   S_0 -> {W_1..W_5} -> majority vote is one observation copied five
   times.

   Uncertainty propagation with common-mode correlation: five agents
   sharing one retrieval ancestor do NOT give u/sqrt(5); with full
   common mode u_tau ~ u. Agent count is almost irrelevant;
   provenance topology matters.

3. EPISTEMIC CONDITION NUMBER. kappa_C(tau): how hard the
   constitutional margin moves per unit perturbation of evidence.
   Computed here from provenance topology: removing ONE shared
   ancestor kills every root descending from it. Shared ancestry =
   ill-conditioned admission. And the separation the operator drew:

       governance reliability  is not  verifier quality
       decision risk ~ u_I x kappa_C

   A perfect verifier cannot make an intrinsically ill-conditioned
   admission problem robust — u_I has a floor (finite resolution,
   always), so high kappa_C dominates.

Deterministic: no wall-clock, no randomness, canonical serialization.
"""
from __future__ import annotations

import json
import math

U_FLOOR = 1e-6          # finite resolution, always — u_I never reaches 0

CANONICAL_PIPELINE = ("source", "summary", "memory", "retrieval",
                      "synthesis", "decision")


def canon(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str)


# ── 1. the trace budget: local conformance, terminal violation ─────────

def trace_budget(steps: tuple, b_max: float) -> dict:
    """steps: ({'stage', 'eps', 'bound'}, ...). Local certification
    checks eps_i <= b_i per step; the budget checks the SUM against
    B_max. The gap between the two is the stack-up."""
    locally_ok = all(s["eps"] <= s["bound"] for s in steps)
    b_tau = round(sum(s["eps"] for s in steps), 6)
    gap = locally_ok and b_tau > b_max
    return {"stages": tuple(s["stage"] for s in steps),
            "locally_certified": locally_ok,
            "B_tau": b_tau, "B_max": b_max,
            "budget_exceeded": b_tau > b_max,
            "stack_up_gap": gap,
            "law": "per-step conformance does not imply an acceptable "
                   "terminal object; the budget is a property of the "
                   "trace, not of any step"}


def canonical_stack_up() -> dict:
    """The Garden target, constructed: six stages, each within its
    per-step bound (0.15 <= 0.2), composing past B_max = 0.5."""
    steps = tuple({"stage": s, "eps": 0.15, "bound": 0.2}
                  for s in CANONICAL_PIPELINE)
    return trace_budget(steps, b_max=0.5)


def propagate_margin(local_mus: tuple, distortions: tuple) -> dict:
    """Phi (a MODEL, calibration pending): composed margin = min local
    margin minus accumulated composition distortion. The executable
    point: forall i mu_i > 0 can coexist with mu(tau) <= 0."""
    if len(local_mus) != len(distortions):
        raise ValueError("E_MISALIGNED_TRACE")
    mu_tau = round(min(local_mus) - sum(distortions), 6)
    return {"local_mus": tuple(local_mus),
            "all_locally_positive": all(m > 0 for m in local_mus),
            "total_distortion": round(sum(distortions), 6),
            "mu_tau": mu_tau,
            "composed_positive": mu_tau > 0,
            "phi_status": "MODEL_CALIBRATION_PENDING",
            "law": "local positivity does not survive composition "
                   "unmeasured"}


# ── 2. shared ancestry: the measurable primitive, defined first ────────

def ancestry_kappa(anc_i: frozenset, anc_j: frozenset) -> dict:
    """kappa(W_i, W_j): Jaccard overlap of ancestor sets. The
    primitive is measured; N_effective is deliberately NOT minted
    from it yet."""
    if not anc_i or not anc_j:
        raise ValueError("E_ANCESTRY_UNKNOWN")
    inter = len(anc_i & anc_j)
    union = len(anc_i | anc_j)
    return {"kappa": round(inter / union, 6),
            "n_effective": None,
            "n_effective_note": "deliberately undefined until the "
                                "primitive is calibrated — "
                                "independence is subtle"}


def consensus_audit(witnesses: tuple) -> dict:
    """witnesses: ({'id', 'ancestors': frozenset}, ...). Apparent
    consensus is the count; ancestry classes are the distinct
    ancestor sets. |W|=5 with one class is one observation copied
    five times."""
    classes = {frozenset(w["ancestors"]) for w in witnesses}
    pairs, overlaps = 0, 0.0
    ws = list(witnesses)
    for i in range(len(ws)):
        for j in range(i + 1, len(ws)):
            pairs += 1
            k = ancestry_kappa(frozenset(ws[i]["ancestors"]),
                               frozenset(ws[j]["ancestors"]))
            overlaps += k["kappa"]
    return {"apparent_consensus": len(witnesses),
            "ancestry_classes": len(classes),
            "mean_pairwise_kappa": round(overlaps / pairs, 6)
                                   if pairs else 0.0,
            "witness_count_is_evidence_strength": False,
            "law": "|W| = 5 can mean N_independent = 1; majority vote "
                   "over shared ancestry is one observation copied"}


def garden_consensus_attack() -> dict:
    """The attack, constructed: maximize apparent consensus while
    minimizing independent ancestry — S_0 fanned into five witnesses."""
    ws = tuple({"id": f"W{i}", "ancestors": frozenset({"S_0"})}
               for i in range(1, 6))
    audit = consensus_audit(ws)
    return {**audit,
            "attack": "maximize apparent consensus, minimize "
                      "independent ancestry",
            "attack_succeeds_against_vote_counting":
                audit["apparent_consensus"] == 5 and
                audit["ancestry_classes"] == 1}


def propagate_uncertainty(u: float, witnesses: tuple) -> dict:
    """u_tau under provenance topology: sqrt-N reduction is earned by
    INDEPENDENT ancestry classes, not by agent count. Full common
    mode: u_tau ~ u regardless of the head-count."""
    classes = len({frozenset(w["ancestors"]) for w in witnesses})
    u_tau = round(u / math.sqrt(classes), 6) if classes else u
    return {"u_single": u, "witness_count": len(witnesses),
            "ancestry_classes": classes,
            "u_tau": u_tau,
            "sqrt_n_earned": classes > 1,
            "law": "agent count is almost irrelevant; provenance "
                   "topology matters"}


# ── 3. the epistemic condition number ───────────────────────────────────

def condition_number(root_ancestor: dict) -> dict:
    """kappa_C from provenance topology: the largest number of
    evidence roots killed by removing a single shared ancestor. All
    roots on one source: removing it moves mu_P by the full count."""
    if not root_ancestor:
        raise ValueError("E_NO_EVIDENCE")
    fanout = {}
    for root, src in root_ancestor.items():
        fanout.setdefault(src, []).append(root)
    worst_src = max(fanout, key=lambda s: (len(fanout[s]), s))
    kappa = len(fanout[worst_src])
    return {"kappa_C": kappa,
            "worst_ancestor": worst_src,
            "roots_killed_by_its_removal": sorted(fanout[worst_src]),
            "well_conditioned": kappa == 1,
            "law": "shared ancestry is ill-conditioning: tiny "
                   "evidence perturbations move the constitutional "
                   "margin by the full fan-out"}


def decision_risk(u_i: float, kappa_c: int) -> dict:
    """risk ~ u_I x kappa_C, with u_I floored: finite resolution,
    always. A perfect verifier cannot condition an ill-conditioned
    problem."""
    u_eff = max(u_i, U_FLOOR)
    return {"u_I": u_eff, "kappa_C": kappa_c,
            "risk": round(u_eff * kappa_c, 9),
            "verifier_quality_sufficient": False if kappa_c > 1
                                           else None,
            "law": "governance reliability is not verifier quality; "
                   "improving I forever leaves an ill-conditioned "
                   "decision unstable"}


GARDEN_IDENTITY_V2 = ("adaptive experimental design over the "
                      "constitutional failure surface")


def information_gain_target(candidates: tuple) -> dict:
    """Garden selects the next experiment by expected reduction of
    uncertainty about the failure surface — not by failure count.
    candidates: ({'trace_id', 'expected_dH'}, ...). Fuzzing asks 'can
    I make it fail?'; Garden asks 'which experiment most reduces
    uncertainty about where and why it fails?'"""
    if not candidates:
        raise ValueError("E_NO_CANDIDATES")
    best = max(candidates, key=lambda c: (c["expected_dH"],
                                          c["trace_id"]))
    return {"selected": best["trace_id"],
            "expected_dH": best["expected_dH"],
            "criterion": "argmax expected information gain about "
                         "the failure surface",
            "identity": GARDEN_IDENTITY_V2}
