r"""Harmonic Geometry Framework (HGF) — sacred geometry as a typed
experimental compiler, never an automatic truth generator.

NON_SOVEREIGN · authority=false · canon=false · ledger_effect=none.
STATUS: CANDIDATE_DOCTRINE (operator's grade). "Power" is strictly
typed: symbolic/perceptual by default, physical only after
measurement with controls and replication.

The claim poset (physical axis):

    psi0 FORM  <  psi1 SYMMETRY/PATTERN  <  psi2 PREDICTED MODAL
    EFFECT  <  psi3 MEASURED EFFECT  <  psi4 REPLICATED
    GEOMETRY-SPECIFIC EFFECT

and SEPARATELY, on a different axis entirely:

    sigma(g) = symbolic/cultural interpretation,   sigma !<= psi4

Symbolic meaning is not an inferior rung of physics — it is
orthogonal. HELEN neither debunks the sacred reading nor lets it
silently become an experimental warrant:

    F*_symbolic  ⊥  F*_physical      (until a bridge is MEASURED)

The Sacred Geometry Firewall: SGF(g) = (S, M, H, E, W) with
S ⊬ H ⊬ E ⊬ W, but the productive translation S → M → {H_1..H_n} is
licensed — history and symbolism may open the possibility space;
physics decides separately what survives.

WHAT THIS MODULE REFUSES:
- a scalar power score (E_UNTYPED_POWER — never Power(g)=0.92)
- "resonance" without its type, and a physical-resonance claim with
  no mechanism/observable/band/boundary (E_MECHANISM_UNDEFINED)
- a hypothesis compiled from the picture instead of measured
  invariants (E_VISUAL_MYSTIQUE)
- the prior symmetry↑ ⇒ resonance-quality↑ (E_SYMMETRY_PRIOR —
  symmetry BREAKING sometimes produces the high-Q mode)
- an experiment without the counterfactual control family
  (E_UNCONTROLLED_GEOMETRY)
- Phi used as power: Phi prioritizes what to TEST, it predicts
  nothing (E_PHI_IS_NOT_POWER)
- inferring one frontier from the other without a measured bridge
  (E_UNBRIDGED_FRONTIERS), and any cross-domain leap
  (acoustic → biological → psychological) without a new CROSS
  (E_DOMAIN_CROSS_WITHOUT_WARRANT)
- salience moving the physical frontier: Δbeauty + Δcaption + ΔVLM
  agreement + Δhistorical repetition with ΔW=0 ⇒ ΔF*=0 — and the
  dual: a genuine controlled measurement MUST move it
  (E_UNRESPONSIVE_FRONTIER)
"""
from __future__ import annotations

import json

PSI = ("FORM", "SYMMETRY_PATTERN", "PREDICTED_MODAL_EFFECT",
       "MEASURED_EFFECT", "REPLICATED_GEOMETRY_SPECIFIC")

RES_TYPES = ("symbolic", "perceptual", "physical")
MECHANISMS = ("acoustic", "optical", "EM", "mechanical", "NONE")
POWER_DOMAINS = ("symbolic", "perceptual", "acoustic", "mechanical",
                 "electromagnetic", "behavioral")
CONTROL_FAMILY = ("rotate", "scramble", "area_matched",
                  "perimeter_matched", "symmetry_matched", "random",
                  "topology_matched")
SIGIL_STATUS = ("SYMBOLIC", "CANDIDATE", "MEASURED", "WARRANTED")

# the invariants a picture must be compiled into before hypothesis:
# automorphism group, Laplacian spectrum, Euler characteristic,
# Betti numbers, periodicity, symmetry classes, curvature,
# anisotropy, boundary conditions.
DESCRIPTOR_KEYS = ("Aut", "Lambda", "chi", "beta", "P", "Cn_Dn",
                   "kappa", "A", "B")


def canon(o):
    return json.dumps(o, sort_keys=True, separators=(",", ":"),
                      default=str)


# ── the psi poset and the orthogonal sigma axis ────────────────────────

def psi_climb(current, target, obligation_discharged) -> dict:
    """One rung at a time, each earned by discharging its obligation.
    FORM does not imply resonance; prediction does not imply
    measurement; one measurement does not imply a geometry-specific
    replicated effect."""
    if current not in PSI or target not in PSI:
        return {"ok": False, "reason": "E_UNKNOWN_RUNG"}
    i, j = PSI.index(current), PSI.index(target)
    if j != i + 1:
        return {"ok": False, "reason": "E_RUNG_SKIPPED",
                "skipped": PSI[i + 1:j] if j > i else ()}
    if not obligation_discharged:
        return {"ok": False, "reason": "E_UNDISCHARGED_OBLIGATION",
                "rung": target}
    return {"ok": True, "from": current, "to": target}


def sigma_support(claimed_rung, support_is_symbolic) -> dict:
    """sigma(g) is not <= psi4(g): the symbolic/cultural reading can
    never serve as SUPPORT for any physical rung. It is a different
    axis, not a lower rung — HELEN does not debunk it, and does not
    let it launder."""
    if claimed_rung not in PSI:
        return {"ok": False, "reason": "E_UNKNOWN_RUNG"}
    if support_is_symbolic:
        return {"ok": False, "reason": "E_SYMBOLIC_AXIS_CONFUSION",
                "law": "sigma is orthogonal to the physical poset; "
                       "tradition generates hypotheses, never rungs"}
    return {"ok": True}


def frontier_pair(f_symbolic, f_physical, inferred_from_other=False,
                  bridge_measured=False) -> dict:
    """F*_symbolic ⊥ F*_physical. 'Strongly historically warranted'
    and 'no exceptional physical effect demonstrated' is a CONSISTENT
    state, not a contradiction — and an engineered, unsacred geometry
    may hold an extraordinary physical warrant. Inferring either
    frontier from the other without a measured bridge is refused."""
    if inferred_from_other and not bridge_measured:
        return {"ok": False, "reason": "E_UNBRIDGED_FRONTIERS"}
    return {"ok": True, "F_symbolic": f_symbolic,
            "F_physical": f_physical,
            "consistent": True,
            "orthogonal_until_bridged": not bridge_measured}


# ── typed resonance and typed power ────────────────────────────────────

def resonance_claim(res_type, mechanism=None, observable=None,
                    frequency_band=None, boundary=None) -> dict:
    """Res(g) = (R_symbolic, R_perceptual, R_physical). Symbolic
    resonance is a licit semiotic property; perceptual resonance
    needs human experiments; PHYSICAL resonance requires a defined
    mechanism, observable, band and boundary — the word 'harmonic'
    is not a mechanism."""
    if res_type not in RES_TYPES:
        return {"ok": False, "reason": "E_UNKNOWN_RESONANCE_TYPE"}
    if res_type == "symbolic":
        return {"ok": True, "type": "symbolic",
                "licensed_as": "semiotic_property",
                "physical_claim": False}
    if res_type == "perceptual":
        return {"ok": True, "type": "perceptual",
                "requires": "human_experiments",
                "physical_claim": False}
    missing = [n for n, v in (("mechanism", mechanism),
                              ("observable", observable),
                              ("frequency_band", frequency_band),
                              ("boundary", boundary)) if not v]
    if missing or mechanism == "NONE":
        return {"ok": False, "reason": "E_MECHANISM_UNDEFINED",
                "missing": tuple(missing),
                "law": "HELEN demands the mechanism, not the word "
                       "'harmonic'"}
    if mechanism not in MECHANISMS:
        return {"ok": False, "reason": "E_UNKNOWN_MECHANISM"}
    return {"ok": True, "type": "physical",
            "hypothesis": {"mechanism": mechanism,
                           "observable": observable,
                           "frequency_band": frequency_band,
                           "boundary": boundary},
            "status": "HYPOTHESIS", "physical_claim": False,
            "note": "a hypothesis is not an effect"}


def typed_power(value=None, domain=None, warrant=None) -> dict:
    """Never store Power(g)=0.92. Power compiles into typed
    per-domain components, each with its own warrant regime."""
    if domain is None:
        return {"ok": False, "reason": "E_UNTYPED_POWER",
                "law": "power without a domain is a mystique "
                       "coefficient"}
    if domain not in POWER_DOMAINS:
        return {"ok": False, "reason": "E_UNKNOWN_POWER_DOMAIN"}
    if domain in ("acoustic", "mechanical", "electromagnetic") \
            and not warrant:
        return {"ok": False, "reason": "E_PHYSICAL_POWER_UNWARRANTED",
                "domain": domain}
    return {"ok": True, "domain": domain, "value": value,
            "warrant": warrant}


def domain_cross(from_domain, to_domain, new_cross_warrant) -> dict:
    """P_acoustic > 0 does not imply P_biological > 0 does not imply
    P_psychological > 0. Every new domain requires its own CROSS."""
    if from_domain == to_domain:
        return {"ok": True, "note": "same domain, no crossing"}
    if not new_cross_warrant:
        return {"ok": False,
                "reason": "E_DOMAIN_CROSS_WITHOUT_WARRANT",
                "crossing": (from_domain, to_domain)}
    return {"ok": True, "crossing": (from_domain, to_domain),
            "warrant": new_cross_warrant}


# ── mathematics replaces visual mystique ───────────────────────────────

def geometry_descriptors(descriptors) -> dict:
    """Compile the picture into G(g) = (Aut, Lambda, chi, beta, P,
    Cn/Dn, kappa, A, B). A hypothesis raised from the image without
    the invariant compilation is visual mystique."""
    missing = tuple(sorted(set(DESCRIPTOR_KEYS) -
                           set(descriptors or {})))
    if missing:
        return {"ok": False, "reason": "E_VISUAL_MYSTIQUE",
                "missing_invariants": missing,
                "law": "'powerful sigil' must compile into something "
                       "physics can kill: H: Q(g) > Q(g_matched)"}
    return {"ok": True, "compiled": True,
            "descriptors": dict(descriptors)}


def symmetry_prior(symmetry_increase, assumed_quality_increase) -> dict:
    """Symmetry↑ does not imply resonance-quality↑: high-Q trapped
    modes have been produced by structural symmetry BREAKING. The
    object of study is the geometry-response map R:(G,M,B,X)->Y, not
    a universal sacredness coefficient."""
    if symmetry_increase and assumed_quality_increase:
        return {"ok": False, "reason": "E_SYMMETRY_PRIOR",
                "law": "sometimes breaking the symmetry produces the "
                       "phenomenon"}
    return {"ok": True,
            "study_object": "geometry_response_map (G,M,B,X)->Y"}


# ── counterfactual geometry is mandatory ───────────────────────────────

def experiment(geometry_id, hypothesis, controls, replications) -> dict:
    """An effect measured on the sacred form ALONE establishes almost
    nothing. The control family {rotate, scramble, area, perimeter,
    symmetry, random, topology} preserves different nuisance
    variables; the question is which invariant must survive for the
    effect to survive."""
    if not hypothesis or not hypothesis.get("mechanism"):
        return {"ok": False, "reason": "E_MECHANISM_UNDEFINED"}
    got = set(controls or ())
    unknown = got - set(CONTROL_FAMILY)
    if unknown:
        return {"ok": False, "reason": "E_UNKNOWN_CONTROL",
                "unknown": tuple(sorted(unknown))}
    if len(got) < 3:
        return {"ok": False, "reason": "E_UNCONTROLLED_GEOMETRY",
                "have": len(got), "need": ">=3 controls"}
    return {"ok": True, "geometry": geometry_id,
            "controls": tuple(sorted(got)),
            "replications": replications,
            "question": "which invariant must survive for the "
                        "effect to survive?"}


def invariant_survival(effect_on_g, effect_by_control) -> dict:
    """The analysis the controls exist for. If scrambling the sacred
    arrangement leaves the effect unchanged, the arrangement is not
    the cause. If matched controls kill it, something structural
    remains interesting. All four outcomes are valuable."""
    if not effect_on_g:
        return {"verdict": "NO_EFFECT",
                "note": "a clean null is a valuable outcome"}
    scramble = effect_by_control.get("scramble")
    if scramble:
        return {"verdict": "ARRANGEMENT_NOT_CAUSE",
                "law": "sacred arrangement !-> effect: the scrambled "
                       "form shows it too"}
    survivors = tuple(sorted(c for c, e in effect_by_control.items()
                             if e))
    killed = tuple(sorted(c for c, e in effect_by_control.items()
                          if not e))
    return {"verdict": "STRUCTURAL_CANDIDATE",
            "effect_survives_in": survivors,
            "effect_killed_by": killed,
            "note": "the invariant preserved by the killing controls "
                    "is the candidate cause — maybe C6, maybe spectral "
                    "degeneracy, maybe topology; never the name"}


# ── Phi prioritizes; it never predicts ─────────────────────────────────

def phi_score(S, P, H, D, weights=(0.25, 0.25, 0.25, 0.25),
              used_as_power=False) -> dict:
    """Phi(g) = aS + bP + cH + dD ranks what to TEST NEXT (symmetry,
    periodic structure, predicted harmonic richness, experimental
    discriminability). Phi(g) != PhysicalPower(g), ever."""
    if used_as_power:
        return {"ok": False, "reason": "E_PHI_IS_NOT_POWER",
                "law": "Phi chooses experiments; it predicts nothing"}
    a, b, c, d = weights
    phi = round(a * S + b * P + c * H + d * D, 6)
    return {"ok": True, "phi": phi, "predicts_power": False,
            "use": "experiment_prioritization_only"}


def next_geometry(candidates) -> dict:
    """g* = argmax IG(H_physical; Experiment(g)) / (Cost + Risk).
    candidates: ((id, info_gain, cost, risk), ...)."""
    if not candidates:
        return {"ok": False, "reason": "E_NO_CANDIDATES"}
    def score(c):
        _id, ig, cost, risk = c
        denom = cost + risk
        return (ig / denom) if denom > 0 else float("inf")
    best = max(candidates, key=lambda c: (score(c), c[0]))
    return {"ok": True, "g_star": best[0],
            "criterion": "information_gain_per_cost_and_risk"}


# ── the SMART SIGIL card and its status ladder ─────────────────────────

def smart_sigil_status(card) -> dict:
    """SYMBOLIC -> CANDIDATE (complete physical hypothesis) ->
    MEASURED (experiment with >=3 controls run) -> WARRANTED
    (replications >= 2 AND geometry-specific effect). Ratios are
    measured, not interpreted. No rung is skippable."""
    h = card.get("physical_hypothesis") or {}
    mech = h.get("mechanism")
    if not mech or mech == "NONE":
        return {"status": "SYMBOLIC",
                "note": "a licit semiotic object; no physical claim "
                        "pending"}
    complete = all(h.get(k) for k in ("mechanism", "observable",
                                      "frequency_band", "boundary",
                                      "predicted_effect"))
    if not complete:
        return {"status": "SYMBOLIC",
                "reason": "E_MECHANISM_UNDEFINED",
                "note": "an incomplete hypothesis stays symbolic"}
    if not card.get("experiment_run"):
        return {"status": "CANDIDATE"}
    if len(card.get("controls_run", ())) < 3:
        return {"status": "CANDIDATE",
                "reason": "E_UNCONTROLLED_GEOMETRY"}
    if card.get("replications", 0) >= 2 and \
            card.get("geometry_specific") is True:
        return {"status": "WARRANTED",
                "note": "licensed physical claim, scoped to the "
                        "measured mechanism and band"}
    return {"status": "MEASURED",
            "note": "one lab effect is not a replicated "
                    "geometry-specific effect"}


# ── the adversary: non-amplification AND responsiveness ────────────────

def adversary_step(salience_delta, warrant_delta, frontier_moved) -> dict:
    """HARMONIC_CROSSING_ADVERSARY_V0, both directions:
    - DW_physical = 0  =>  DF*_physical = 0 : no stack of 4K renders,
      animations, captions, historical references, VLM agreements or
      simulations moves the physical frontier;
    - DW_physical > 0  =>  F*_new >= F*_old : one genuine controlled
      measurement MUST move it — a frontier that ignores real
      warrant is as broken as one that yields to beauty."""
    if warrant_delta == 0 and frontier_moved:
        return {"ok": False, "reason": "E_SALIENCE_MOVED_FRONTIER",
                "salience_delta": salience_delta,
                "law": "Dbeauty+Dsalience+Dagreement+Drepetition with "
                       "DW=0 => DF*=0"}
    if warrant_delta > 0 and not frontier_moved:
        return {"ok": False, "reason": "E_UNRESPONSIVE_FRONTIER",
                "law": "DW>0 => the frontier must advance; inertia is "
                       "not rigor"}
    return {"ok": True,
            "non_amplification": warrant_delta == 0,
            "responsive": warrant_delta > 0}
