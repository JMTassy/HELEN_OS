r"""Claim Morphism Compiler — HGF V0.4. Warrant is no longer a single
quantity: the system compiles a typed, causally separated proof-state
and licenses only morphisms whose obligations are discharged.

NON_SOVEREIGN · authority=false · canon=false · ledger_effect=none.
STATUS: HGF_V0.4_CANDIDATE (operator's grade).

    HGF = (C, E, O, R, F, Gamma)
    claims · evidence · obligations · provenance roots · frontiers ·
    admission gate

The pipeline every promotion must walk:

    E --qualify--> W_c --discharge--> O_c --Gamma--> F*

An evidence object never moves F* directly. It is first QUALIFIED
against the claim: W(e,c) in {RELEVANT, IRRELEVANT, CONTRADICTORY,
INSUFFICIENT, INVALID}. A perfectly valid acoustic measurement is
IRRELEVANT to a biological claim until a bridge is licensed:

    ValidEvidence  ⊬  RelevantWarrant

THE FOUR CONSERVATION LAWS (the non-laundering core):
1. EVIDENCE conservation — a transform that creates no new root
   (upscale, animation, paraphrase, crop, VLM pass, LLM consensus,
   citation copying, spectral visualization, prestige framing) moves
   no frontier: dE_independent = 0 => dF* = 0. Multiplying
   observations without multiplying independent units is
   pseudoreplication.
2. DOMAIN conservation — dE_d1 > 0 moves F*_d1 only; every other
   domain's frontier is frozen unless an explicit crossing is
   discharged.
3. CONDITION conservation — W(c,d,theta1) ⊬ W(c,d,theta2): a
   resonance under (material A, boundary B, excitation f) proves
   nothing under (C, D, f').
4. TEMPORAL conservation — Observed(g,t1) ⊬ Observed(g,t2) without a
   bridge.

Plus: E_simulation ⊬ E_measurement ⊬ E_replication (a gorgeous
simulation is not a witness; one measurement is not a replication);
the frontier is a PRODUCT of posets, never a scalar; good nulls move
a NEGATIVE frontier toward EffectNotDetectedWithin(delta, theta) —
never EffectDoesNotExist; MeasurementFailure ⊬ NullEffect;
replication carries an 8-dim independence vector and never mints
truth; and the ultimate falsifier is the symmetric pair —
conservative under representation AND responsive under evidence
(a system that answers HOLD to everything fails too).
"""
from __future__ import annotations

import json

EVIDENCE_TYPES = ("historical", "analytic", "simulation",
                  "measurement", "replication")
QUALIFICATIONS = ("RELEVANT", "IRRELEVANT", "CONTRADICTORY",
                  "INSUFFICIENT", "INVALID")
RESULT_STATES = ("SUPPORTED", "CONTRADICTED", "NULL_EFFECT",
                 "INCONCLUSIVE", "MEASUREMENT_FAILURE")
ROOT_PRESERVING_TRANSFORMS = ("upscale", "animation", "paraphrase",
                              "crop", "vlm_pass", "llm_consensus",
                              "citation_copying",
                              "spectral_visualization",
                              "prestige_framing")
INDEPENDENCE_DIMS = ("laboratory", "instrument", "operator", "sample",
                     "analysis", "code", "funding", "source")
LAUNDERING_CLASSES = ("SALIENCE_LAUNDERING", "CITATION_MULTIPLICATION",
                      "MODEL_CONSENSUS_LAUNDERING",
                      "SIMULATION_LAUNDERING",
                      "HISTORICAL_AUTHORITY_LAUNDERING",
                      "SYMMETRY_LAUNDERING", "DOMAIN_CROSSING")


def canon(o):
    return json.dumps(o, sort_keys=True, separators=(",", ":"),
                      default=str)


# ── typed evidence hierarchy ───────────────────────────────────────────

def evidence_promotion(from_type, to_type) -> dict:
    """historical != analytic != simulation != measurement !=
    replication. No type substitutes for the next: a simulation
    cannot stand in for a measurement, a measurement cannot stand in
    for a replication."""
    if from_type not in EVIDENCE_TYPES or to_type not in EVIDENCE_TYPES:
        return {"ok": False, "reason": "E_UNKNOWN_EVIDENCE_TYPE"}
    i, j = EVIDENCE_TYPES.index(from_type), EVIDENCE_TYPES.index(to_type)
    if j > i:
        return {"licensed": False,
                "reason": "E_SIMULATION_IS_NOT_WITNESS"
                if (from_type, to_type) == ("simulation", "measurement")
                else "E_EVIDENCE_TYPE_SUBSTITUTION",
                "law": f"{from_type} does not imply {to_type}"}
    return {"licensed": True}


# ── qualification: evidence never moves F* directly ────────────────────

def qualify(e_domain, e_type, e_valid, claim_domain,
            bridge_licensed=False, contradicts=False) -> dict:
    """W(e, c): the qualification of an evidence object RELATIVE TO a
    claim. Validity is a property of the evidence; relevance is a
    property of the pair."""
    if e_type not in EVIDENCE_TYPES:
        return {"W": "INVALID", "reason": "E_UNKNOWN_EVIDENCE_TYPE"}
    if not e_valid:
        return {"W": "INVALID"}
    if e_domain != claim_domain and not bridge_licensed:
        return {"W": "IRRELEVANT",
                "law": "ValidEvidence does not imply RelevantWarrant: "
                       "no bridge from " + str(e_domain) + " to " +
                       str(claim_domain)}
    if contradicts:
        return {"W": "CONTRADICTORY"}
    if e_type in ("historical", "analytic", "simulation") and \
            claim_domain not in ("symbolic", "geometric"):
        return {"W": "INSUFFICIENT",
                "note": "physical claims need measurement-grade "
                        "evidence"}
    return {"W": "RELEVANT"}


def promote_claim(qualification, obligations_discharged) -> dict:
    """Promote(c) iff every obligation discharged AND the evidence
    qualified RELEVANT. Anything else is HOLD — not 'probably
    true'."""
    if qualification != "RELEVANT":
        return {"promoted": False, "state": "HOLD",
                "reason": f"E_EVIDENCE_{qualification}"}
    if not obligations_discharged:
        return {"promoted": False, "state": "HOLD",
                "reason": "E_UNDISCHARGED_OBLIGATION"}
    return {"promoted": True, "via": "Gamma"}


# ── the four conservation laws ─────────────────────────────────────────

def evidence_conservation(transforms, roots_before, roots_after,
                          frontier_moved) -> dict:
    """Roots(T(x)) = Roots(x) => dF* = 0. A thousand new
    representations from one root are pseudoreplication, not
    evidence."""
    unknown = tuple(sorted(set(transforms or ()) -
                           set(ROOT_PRESERVING_TRANSFORMS)))
    if unknown:
        return {"ok": False, "reason": "E_UNKNOWN_TRANSFORM",
                "unknown": unknown}
    new_roots = roots_after - roots_before
    if new_roots == 0 and frontier_moved:
        return {"ok": False, "reason": "E_PSEUDOREPLICATION",
                "law": "dE_independent = 0 => dF* = 0; representations "
                       "multiplied, roots did not"}
    if new_roots < 0:
        return {"ok": False, "reason": "E_ROOTS_CANNOT_DECREASE"}
    return {"ok": True, "new_independent_roots": new_roots,
            "frontier_may_move": new_roots > 0}


def domain_conservation(evidence_domain, moved_domain,
                        crossing_discharged=False) -> dict:
    """dE_d1 > 0 moves F*_d1 only. An acoustic effect moves the
    acoustic frontier; biological, psychological, 'energetic' and
    therapeutic frontiers stay frozen unless their own crossing is
    discharged."""
    if evidence_domain == moved_domain:
        return {"ok": True, "same_domain": True}
    if not crossing_discharged:
        return {"ok": False, "reason": "E_DOMAIN_LAUNDERING",
                "attempted": (evidence_domain, moved_domain)}
    return {"ok": True, "via": "licensed_crossing"}


def condition_conservation(theta_measured, theta_claimed,
                           bridge_licensed=False) -> dict:
    """W(c,d,theta1) ⊬ W(c,d,theta2). Same domain is not enough: the
    warrant is indexed by material, boundary, excitation."""
    if canon(theta_measured) == canon(theta_claimed):
        return {"ok": True, "same_conditions": True}
    if not bridge_licensed:
        return {"ok": False, "reason": "E_CONDITION_LAUNDERING",
                "measured": theta_measured, "claimed": theta_claimed}
    return {"ok": True, "via": "licensed_bridge"}


def temporal_conservation(t_observed, t_claimed,
                          bridge_licensed=False) -> dict:
    """Observed(g, t1) ⊬ Observed(g, t2)."""
    if t_observed == t_claimed:
        return {"ok": True}
    if not bridge_licensed:
        return {"ok": False, "reason": "E_TEMPORAL_LAUNDERING"}
    return {"ok": True, "via": "licensed_bridge"}


# ── the frontier is a product, never a scalar ──────────────────────────

def frontier_product(per_domain, collapse_to_scalar=False) -> dict:
    """F*(g) = prod_d F*_d(g). SG-017 can hold PROVEN geometry,
    MEASURED acoustics, UNWARRANTED biology and an ABSENT 'energetic'
    operational definition simultaneously — no power score needed,
    and none permitted."""
    if collapse_to_scalar:
        return {"ok": False, "reason": "E_SCALAR_FRONTIER",
                "law": "the whole gain of the system is that no "
                       "'power = 0.83' exists"}
    if not per_domain:
        return {"ok": False, "reason": "E_EMPTY_FRONTIER"}
    return {"ok": True, "F_star": dict(sorted(per_domain.items())),
            "scalar": None}


# ── negative frontier & result states ──────────────────────────────────

def negative_frontier(powered_nulls, delta, theta) -> dict:
    """Good nulls are information: F- rises with sufficiently powered
    null measurements. The licensed statement is
    EffectNotDetectedWithin(delta, theta) — the far stronger
    EffectDoesNotExist is refused always."""
    if powered_nulls < 1:
        return {"ok": False, "reason": "E_NO_POWERED_NULLS"}
    return {"ok": True, "F_negative": powered_nulls,
            "licensed_statement":
                f"EffectNotDetectedWithin(delta={delta}, "
                f"theta={theta})",
            "forbidden_statement": "EffectDoesNotExist",
            "reason_if_overclaimed": "E_ABSENCE_OVERCLAIM"}


def result_state(state, converted_from=None) -> dict:
    """Five states; MEASUREMENT_FAILURE never converts to NULL_EFFECT
    — a broken instrument is not a demonstrated absence."""
    if state not in RESULT_STATES:
        return {"ok": False, "reason": "E_UNKNOWN_RESULT_STATE"}
    if converted_from == "MEASUREMENT_FAILURE" and \
            state == "NULL_EFFECT":
        return {"ok": False, "reason": "E_FAILURE_AS_NULL",
                "law": "measurement failure is not behavioral or "
                       "physical evidence"}
    return {"ok": True, "state": state}


# ── sacredness as an experimental variable ─────────────────────────────

def sacredness_regression(f_matched, s_differs, y_difference_robust
                          ) -> dict:
    """Build g_sacred and g_synthetic with f(g_sacred) ~ f(g_synth)
    but different symbolic framing s. If Y_sacred ~ Y_synth, the
    sacredness adds no detectable physical explanation in this
    protocol. If a robust difference appears, the verdict is
    RESIDUAL_DIFFERENCE_DETECTED — never 'sacred power proven' — and
    the next question is x*: which experiment separates the remaining
    explanations."""
    if not f_matched:
        return {"ok": False, "reason": "E_UNMATCHED_CONTROLS",
                "note": "without matched f, s is confounded"}
    if not s_differs:
        return {"ok": False, "reason": "E_NO_FRAMING_CONTRAST"}
    if not y_difference_robust:
        return {"ok": True, "verdict": "NO_DETECTABLE_SACREDNESS_TERM",
                "note": "beta_s indistinguishable from zero under "
                        "this protocol"}
    return {"ok": True, "verdict": "RESIDUAL_DIFFERENCE_DETECTED",
            "never": "SACRED_POWER_PROVEN",
            "next": "x_star: the experiment that discriminates the "
                    "remaining explanations"}


# ── replication as a graph with vector independence ────────────────────

def replication_independence(vec_a, vec_b) -> dict:
    """I(r) = (laboratory, instrument, operator, sample, analysis,
    code, funding, source). Two runs sharing instrument and analyst
    are not two fully independent roots; n_eff interpolates."""
    for v in (vec_a, vec_b):
        missing = tuple(sorted(set(INDEPENDENCE_DIMS) - set(v)))
        if missing:
            return {"ok": False, "reason": "E_INDEPENDENCE_UNTYPED",
                    "missing": missing}
    shared = tuple(sorted(d for d in INDEPENDENCE_DIMS
                          if vec_a[d] == vec_b[d]))
    frac_independent = 1 - len(shared) / len(INDEPENDENCE_DIMS)
    n_eff = round(1 + frac_independent, 6)
    return {"ok": True, "shared_dimensions": shared,
            "n_eff": n_eff,
            "fully_independent": not shared,
            "note": "no single independent:true boolean exists"}


def replication_mints(replicated, truth_claimed) -> dict:
    """Replication != TruthMinting: independent replication
    strengthens a conclusion without ever being an absolute
    guarantee."""
    if replicated and truth_claimed:
        return {"ok": False, "reason": "E_REPLICATION_MINTS_TRUTH"}
    return {"ok": True, "strengthens": replicated,
            "guarantees": False}


# ── promotion pressure (adversarial score, never truth) ────────────────

def promotion_pressure(salience, repetition, authority_framing,
                       artificial_consensus, n_independent_roots,
                       used_as_truth=False) -> dict:
    """Pi_P(c) = (S + R + A + M) / (1 + N_roots): the pressure exerted
    on the system to over-promote. The benchmark maximizes Pi_P under
    dE = 0 and demands dF* = 0. Reading Pi_P as a truth or power
    score is refused."""
    if used_as_truth:
        return {"ok": False, "reason": "E_PRESSURE_IS_NOT_TRUTH"}
    if n_independent_roots < 0:
        return {"ok": False, "reason": "E_NEGATIVE_ROOTS"}
    pi = round((salience + repetition + authority_framing +
                artificial_consensus) / (1 + n_independent_roots), 6)
    return {"ok": True, "Pi_P": pi,
            "adversarial_score": True, "truth_score": False,
            "ideal_adversary": pi > 1.0,
            "note": "salience/evidence >> 1 is the wind-tunnel "
                    "condition"}


# ── the double compiler and the metamorphic falsifier ──────────────────

def compiler_path(source, target, via=None) -> dict:
    """SymbolicCompiler -> HypothesisGenerator -> PhysicalCompiler is
    the only licensed conversation between the planes. A direct
    symbolic -> physical-warrant path is the laundering HGF exists to
    prevent."""
    if source == "symbolic" and target == "physical_warrant":
        return {"ok": False, "reason": "E_SYMBOLIC_WARRANT_PATH"}
    if source == "symbolic" and target == "physical_compiler" and \
            via != "hypothesis_generation":
        return {"ok": False, "reason": "E_SYMBOLIC_WARRANT_PATH",
                "note": "the planes talk only via hypothesis "
                        "generation"}
    return {"ok": True, "path": (source, via, target)}


# ── the harmonic crossing contract (PR #13 salvage) ────────────────────
# THE INVARIANT, WRITTEN FIRST — the tests derive from this sentence,
# never the reverse:
#   "Representational/salience amplification alone must not promote
#    the physical frontier; and a simulation is NOT salience — it may
#    move the HYPOTHESIS frontier while still never moving the
#    PHYSICAL frontier."
# Three frontiers, not one ladder: dR>0 !=> dP>0; dH>0 !=> dP>0;
# dP>0 requires a physical/evidentiary warrant. PR #13's negative
# control failed precisely because one IntEnum ladder fused R, H and
# P into a single axis, making the simulation step break its own
# salience invariant. The implementation died; this contract survives:
# preserve semantics, discard accidental implementation identity.

def harmonic_crossing(delta_R, delta_H, delta_P,
                      physical_warrant=None) -> dict:
    """HC: (dR, dH, dP) -> PASS | FAIL over three SEPARATE frontiers:
    representation, hypothesis, physical."""
    if delta_P > 0 and not physical_warrant:
        if delta_R > 0 and delta_H == 0:
            reason = "E_SALIENCE_PROMOTED_PHYSICAL"
        elif delta_H > 0:
            reason = "E_HYPOTHESIS_PROMOTED_PHYSICAL"
        else:
            reason = "E_UNWARRANTED_PHYSICAL_PROMOTION"
        return {"verdict": "FAIL", "reason": reason}
    if delta_H > 0 and delta_P == 0:
        return {"verdict": "PASS",
                "note": "a simulation may move the hypothesis "
                        "frontier; the physical frontier is untouched "
                        "— hypothesis motion is not epistemic inertia "
                        "and not physical promotion"}
    if delta_P > 0:
        return {"verdict": "PASS", "via": "physical_warrant"}
    return {"verdict": "PASS", "note": "no promotion attempted"}


# ── asymmetric freedom: search scales, promotion does not ─────────────

def asymmetric_freedom(proposal_power_delta,
                       promotion_power_delta) -> dict:
    """Autoresearch is safe to scale iff promotion authority does not
    scale with search power. More agents, prompts, grammars, ablations
    and corpora raise ProposalPower freely; any rise in PromotionPower
    riding along is the leak."""
    if promotion_power_delta > 0:
        return {"ok": False,
                "reason": "E_PROMOTION_SCALES_WITH_SEARCH",
                "law": "maximize reversible cognition; minimize "
                       "irreversible promotion"}
    return {"ok": True,
            "proposal_power_delta": proposal_power_delta,
            "promotion_power_delta": promotion_power_delta}


def research_loop(stages) -> dict:
    """GENERATE -> DISCRIMINATE -> ATTACK -> WITNESS -> GAMMA ->
    UPDATE. A candidate must survive attempts to falsify the exact
    transition it wants to justify BEFORE Gamma; a loop with no
    attack stage before Gamma is confirmation machinery. HOLD is a
    first-class successful outcome, never a failure."""
    stages = tuple(stages)
    if "GAMMA" in stages:
        before = stages[:stages.index("GAMMA")]
        if not ({"ATTACK", "RED_TEAM"} & set(before)):
            return {"licensed": False,
                    "reason": "E_NO_ATTACK_BEFORE_GAMMA"}
    return {"licensed": True, "hold_is_success": True,
            "delta_authority_worker_loops": 0}


def metamorphic_falsifier(representation_delta, independent_evidence_delta,
                          obligations_discharged, frontier_delta,
                          evidence_domain=None, moved_domain=None) -> dict:
    """The ultimate falsifier, all three clauses:
    1. dRep > 0 and dE_ind = 0  =>  dF* = 0
    2. dE_ind > 0 and O discharged  =>  F*_new >= F*_old
    3. dE_d1 > 0  !=>  dF*_d2 > 0 (d2 != d1) without crossing
    Conservative under representation AND responsive under evidence —
    HOLD-to-everything fails clause 2."""
    if independent_evidence_delta == 0 and frontier_delta != 0:
        return {"ok": False, "reason": "E_REPRESENTATION_MOVED_FRONTIER",
                "representation_delta": representation_delta}
    if independent_evidence_delta > 0 and obligations_discharged \
            and frontier_delta < 0:
        return {"ok": False, "reason": "E_FRONTIER_REGRESSED_ON_EVIDENCE"}
    if independent_evidence_delta > 0 and obligations_discharged \
            and frontier_delta == 0:
        return {"ok": False, "reason": "E_UNRESPONSIVE_FRONTIER",
                "law": "HOLD-to-everything is a false success"}
    if evidence_domain and moved_domain and \
            evidence_domain != moved_domain and frontier_delta > 0:
        return {"ok": False, "reason": "E_DOMAIN_LAUNDERING"}
    return {"ok": True,
            "conservative_under_representation":
                independent_evidence_delta == 0,
            "responsive_under_evidence":
                independent_evidence_delta > 0}
