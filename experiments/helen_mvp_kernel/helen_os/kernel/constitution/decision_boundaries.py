r"""Decision Boundaries — the J3 harvest as four CANDIDATE invariants,
a narrow engine, and the J4 reinforcement law.

NON_SOVEREIGN · authority=false · canon=false · ledger_effect=none.
STATUS: every object here is CANDIDATE. promote_to_canon() refuses.

The J3 delta was not documentary volume; it was counterexamples that
changed the SHAPE of the candidate methods — three too-simple rules
became conditional decision operators. The corpus is starting to teach
where to STOP, HOLD and SWITCH, not just how to produce.

THE FOUR CANDIDATES, provisionally frozen for training:

1. TYPED COMMERCIAL STATES.
       ESTIMATE != REQUESTED != LIKELY != APPROVED != CONTRACTED
       != INVOICED != PAID
   No amount enters memory without its state, its date and its
   provenance. No arrow is skipped by narration. (The verified
   pseudo-contradiction was two REQUESTED-state reports one day
   apart, not two incompatible facts.)

2. QUALIFICATION BEFORE ELABORATION. U = (U_r, U_d): reducible vs
   disqualifying uncertainty. Ambiguity does not license work:
       Act(U) = PROBE   if EVSI > C_probe   (bounded)
                HOLD    if admissibility unresolved
                REJECT  if U_d > tau
   Disqualifying uncertainty is checked FIRST — no probe budget is
   spent qualifying what is already out of mandate. (AppsFlyer: the
   HOLD came 39 minutes after the probe proposal, from the same
   decider.)

3. COMMITMENT COUPLING. The governance-debt functional
       D_gov(T) = integral of [C_op(t) - C_econ(t)]_+ dt
   is a research object, not yet an operational metric: measuring it
   REQUIRES a frozen observable codebook for C_op and C_econ
   (E_UNPINNED_CODER otherwise) — the T_m/H_delta/F_b law again. And
   its J4 falsifier is the NEGATIVE: dossiers where debt looks high
   and no measurable friction appears.

4. DYNAMIC COMPARATIVE ADVANTAGE.
       Delta V_t = V(S_t) - V(B_t) - C(S_t)
   recomputed whenever the internal baseline B_t moves. The rule this
   forbids HELEN from learning: "our prototype works, therefore
   continue." Sunk work is not a variable of Delta V.

THE ENGINE, kept narrow. The DECISION BOUNDARY ENGINE reconstructs
OBSERVED surfaces between GO / PROBE / HOLD / REJECT / STOP / SWITCH
— each point carrying the variables KNOWN AT DECISION TIME, the
evidence, and the later outcome when one exists (NO_RECEIPT is a
lawful outcome). It learns decision surfaces, not management slogans;
asking it to "recommend what to do" is out of scope by construction,
and a surface point whose variables include hindsight is refused.

THE J4 REINFORCEMENT LAW (the sharpened falsifier):

    a candidate method is REINFORCED only if it survives a case
    where its predictive variables are present but its expected
    effect is ABSENT

Confirming cases (predictors present, effect present) ACCUMULATE and
never reinforce — correlation does not become doctrine by counting
confirmations. Unexplained successes (predictors absent, effect
present) are boundary information, not support. J4 therefore hunts
failures + counterexamples + NEGATIVE CONTROLS: weak qualification
with a good outcome, high governance debt with no visible cost, an
external solution kept against a strong internal baseline, a LIKELY
budget never approved, an uncertain one contracted fast. The expected
J4 gain is not a new method — it is an estimate of where the J3
methods STOP being valid.

Deterministic: no wall-clock, no randomness, canonical serialization.
"""
from __future__ import annotations

import json

STATUS = "CANDIDATE"

COMMERCIAL_STATES = ("ESTIMATE", "REQUESTED", "LIKELY", "APPROVED",
                     "CONTRACTED", "INVOICED", "PAID")

DECISIONS = ("GO", "PROBE", "HOLD", "REJECT", "STOP", "SWITCH")

ENGINE_SCOPE = "reconstruct observed decision surfaces"
ENGINE_OUT_OF_SCOPE = ("recommend what to do", "rank strategies",
                       "generate management principles")


def canon(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str)


def promote_to_canon(_obj: str) -> dict:
    return {"promoted": False, "reason": "E_CANDIDATE_IS_NOT_CANON",
            "law": "everything in this module is CANDIDATE; canon "
                   "needs a Gamma decision, not a module constant"}


# ── 1. typed commercial states ─────────────────────────────────────────

def typed_amount(state: str, dated: bool, provenance: str | None) -> dict:
    """No amount enters memory without state + date + provenance.
    The amount itself is deliberately NOT a parameter: figures are
    restricted data and live outside this repo; the type travels, the
    number does not."""
    if state not in COMMERCIAL_STATES:
        return {"ok": False, "reason": "E_UNKNOWN_COMMERCIAL_STATE"}
    missing = [k for k, v in (("date", dated), ("provenance",
                                                bool(provenance))) if not v]
    if missing:
        return {"ok": False, "reason": "E_UNTYPED_AMOUNT",
                "missing": sorted(missing)}
    return {"ok": True, "state": state, "provenance": provenance,
            "law": "a number without its state label is a narrative, "
                   "not a datum"}


def state_transition(frm: str, to: str, witness: str | None) -> dict:
    """Forward moves go one arrow at a time, each against a witness.
    No arrow is skipped by narration. Regression (bad news) is lawful
    without permission — reality may demote a state freely."""
    if frm not in COMMERCIAL_STATES or to not in COMMERCIAL_STATES:
        return {"licensed": False, "reason": "E_UNKNOWN_COMMERCIAL_STATE"}
    i, j = COMMERCIAL_STATES.index(frm), COMMERCIAL_STATES.index(to)
    if j <= i:
        return {"licensed": True, "direction": "regression",
                "witness_required": False,
                "law": "bad news needs no permission"}
    if j - i > 1:
        return {"licensed": False, "reason": "E_NARRATIVE_SKIP",
                "skipped": COMMERCIAL_STATES[i + 1:j],
                "law": "no arrow is skipped by narration"}
    if not witness:
        return {"licensed": False, "reason": "E_UNWITNESSED_TRANSITION"}
    return {"licensed": True, "direction": "promotion",
            "frm": frm, "to": to, "witness": witness}


# ── 2. qualification before elaboration ────────────────────────────────

def qualify(u_r: float, u_d: float, tau: float, evsi: float,
            probe_cost: float) -> dict:
    """Act(U). Disqualifying uncertainty first; then the probe pays
    for itself or the file HOLDs."""
    if min(u_r, u_d, tau, probe_cost) < 0:
        raise ValueError("E_NEGATIVE_INPUT")
    if u_d > tau:
        return {"act": "REJECT", "checked_first": "U_d",
                "law": "no probe budget is spent qualifying what is "
                       "already out of mandate"}
    if evsi > probe_cost:
        return {"act": "PROBE", "bounded": True,
                "law": "a probe is bounded or it is not a probe"}
    return {"act": "HOLD",
            "law": "ambiguity does not license work; it licenses a "
                   "qualification decision"}


# ── 3. commitment coupling ─────────────────────────────────────────────

def governance_debt(samples: tuple, coder: dict) -> dict:
    """D_gov = sum of max(0, c_op - c_econ) * dt over samples
    ((c_op, c_econ, dt), ...). Refuses to produce a number without a
    frozen observable codebook — otherwise the integral is tunable."""
    if not coder.get("frozen") or not coder.get("version"):
        return {"measured": False, "reason": "E_UNPINNED_CODER",
                "law": "C_op and C_econ need frozen operational "
                       "coders BEFORE the first measurement, or the "
                       "functional is a tunable number"}
    if not samples:
        raise ValueError("E_NO_SAMPLES")
    debt = sum(max(0.0, op - ec) * dt for op, ec, dt in samples)
    return {"measured": True, "D_gov": round(debt, 6),
            "coder_version": coder["version"],
            "status": "TESTABLE_CANDIDATE_METRIC"}


def debt_negative_control(d_gov: float, frictions_observed: int) -> dict:
    """The J4 hunt: high debt with zero observed friction is not an
    embarrassment to hide — it is the case that bounds the metric's
    validity, and it must be sought on purpose."""
    negative = d_gov > 0 and frictions_observed == 0
    return {"is_negative_control": negative,
            "verdict": "BOUNDS_THE_METRIC" if negative
                       else "CONSISTENT_CASE",
            "law": "a metric untested against its own negatives is a "
                   "correlation wearing a formula"}


# ── 4. dynamic comparative advantage ───────────────────────────────────

def delta_v(v_external: float, v_baseline: float,
            cost_external: float) -> dict:
    """Delta V_t, computed from CURRENT values only. There is no
    sunk-cost parameter, so yesterday's work cannot enter."""
    dv = v_external - v_baseline - cost_external
    return {"delta_V": round(dv, 6),
            "keep_external": dv > 0,
            "act_if_not": "SWITCH",
            "law": "prototype works does not entail continue; the "
                   "baseline is dynamic and sunk work is not a "
                   "variable"}


def baseline_moved(dv_before: float, dv_after: float) -> dict:
    """The Manucurist shape: Delta V positive at t0, the internal
    baseline improves, Delta V goes non-positive — the lawful move is
    to shift capacity to the next differentiating frontier."""
    return {"recomputed": True,
            "was_positive": dv_before > 0,
            "now_positive": dv_after > 0,
            "act": "SWITCH" if (dv_before > 0 >= dv_after) else "KEEP",
            "law": "an external solution does not own a problem; a "
                   "verdict is indexed to the baseline current at "
                   "recomputation"}


# ── the engine, kept narrow ────────────────────────────────────────────

HINDSIGHT_MARKERS = ("outcome", "final_result", "eventual",
                     "in_retrospect")


def surface_point(decision: str, variables_at_decision: dict,
                  evidence: str, outcome: str | None = None) -> dict:
    """One observed point on a decision surface. Variables must have
    been knowable at decision time — a variable named like hindsight
    is refused; NO_RECEIPT is a lawful outcome."""
    if decision not in DECISIONS:
        return {"ok": False, "reason": "E_UNKNOWN_DECISION"}
    if not evidence:
        return {"ok": False, "reason": "E_UNEVIDENCED_POINT"}
    tainted = sorted(k for k in variables_at_decision
                     if any(m in k.lower() for m in HINDSIGHT_MARKERS))
    if tainted:
        return {"ok": False, "reason": "E_HINDSIGHT_VARIABLE",
                "tainted": tainted,
                "law": "a surface learned on hindsight variables "
                       "predicts the past"}
    return {"ok": True, "decision": decision,
            "variables": dict(sorted(variables_at_decision.items())),
            "evidence": evidence,
            "outcome": outcome if outcome is not None else "NO_RECEIPT",
            "status": STATUS}


def engine_task(task: str) -> dict:
    """Surfaces, not slogans. The engine reconstructs observed
    boundaries with their proofs; recommending is out of scope by
    construction, not by discipline."""
    if task in ENGINE_OUT_OF_SCOPE:
        return {"licensed": False, "reason": "E_OUT_OF_SCOPE",
                "scope": ENGINE_SCOPE,
                "law": "the engine learns decision surfaces, not "
                       "management slogans"}
    if task == ENGINE_SCOPE:
        return {"licensed": True, "scope": ENGINE_SCOPE,
                "outputs": ("boundary", "variables_known_at_decision",
                            "evidence", "outcome_if_any")}
    return {"licensed": None, "reason": "E_UNKNOWN_TASK"}


# ── the J4 reinforcement law ───────────────────────────────────────────

def reinforcement(predictors_present: bool, effect_present: bool,
                  survived: bool | None = None) -> dict:
    """A candidate method is reinforced ONLY by surviving a case
    where its predictors are present and its expected effect is
    absent. Everything else is accumulation or boundary data."""
    if predictors_present and effect_present:
        return {"case": "CONFIRMATION", "reinforced": False,
                "accumulates": True,
                "law": "correlation does not become doctrine by "
                       "counting confirmations"}
    if predictors_present and not effect_present:
        if survived is None:
            return {"case": "NEGATIVE_CONTROL", "reinforced": False,
                    "reason": "E_SURVIVAL_UNSCORED",
                    "law": "the negative control must be scored, not "
                           "merely collected"}
        return {"case": "NEGATIVE_CONTROL",
                "reinforced": bool(survived),
                "weakened": not survived,
                "law": "reinforcement is bought only where the "
                       "method could have died"}
    if effect_present:
        return {"case": "UNEXPLAINED_SUCCESS", "reinforced": False,
                "boundary_information": True,
                "law": "an effect without its predictors bounds the "
                       "method; it never supports it"}
    return {"case": "IRRELEVANT", "reinforced": False}


def outcome_attribution(outcome_consistent: bool,
                        causal_path_through_predictors: bool) -> dict:
    """The J4 target-2 lesson. An outcome consistent with a method but
    CAUSED by a variable outside the method's model is a CONFOUNDED
    CONFIRMATION — it supports nothing, and it flags the stratum.

    The instance: a HOLD on a weakly-qualified opportunity followed by
    the opportunity's substrate being destroyed by an exogenous shock.
    The gate 'was right', but through a cause none of its predictors
    carried. Scoring decision rules on a shock-dominated stratum
    without modelling the shock scores the shock, not the rule."""
    if not outcome_consistent:
        return {"case": "DISCONFIRMING_OUTCOME",
                "supports_method": False,
                "note": "route through reinforcement(); this function "
                        "only grades consistent outcomes"}
    if causal_path_through_predictors:
        return {"case": "CONFIRMATION", "supports_method": False,
                "accumulates": True}
    return {"case": "CONFOUNDED_CONFIRMATION",
            "supports_method": False, "accumulates": False,
            "stratum_flag": "EXOGENOUS_SHOCK",
            "law": "an outcome consistent with the method but caused "
                   "outside its model scores the shock, not the rule; "
                   "shock-dominated strata must be modelled or "
                   "excluded"}


BLOCK_OUTCOMES = ("RESUMED", "ABANDONED", "TERMINAL_LOSS")


def block_transition(claimed_outcome: str,
                     outcome_receipt: str | None) -> dict:
    """The J7 counterexample law: BLOCKED_t does not entail
    LOST_{t+Delta}. A HOLD, BLOCK or CANCEL_INTENT is NOT an
    absorbing state — the corpus showed an announced cancellation
    followed eighteen days later by an active budget on the same
    dossier. Promoting a block to any terminal outcome without an
    outcome receipt is refused; with one, it resolves to RESUMED,
    ABANDONED or TERMINAL_LOSS. Recovery trajectories are modeled as
    carefully as failures, or the model overcounts its losses."""
    if claimed_outcome not in BLOCK_OUTCOMES:
        return {"resolved": False, "reason": "E_UNKNOWN_BLOCK_OUTCOME"}
    if not outcome_receipt:
        return {"resolved": False, "state": "OPEN_BLOCKED",
                "absorbing": False,
                "reason": "E_BLOCK_TREATED_AS_ABSORBING",
                "law": "an announced cancellation is an intent, "
                       "never an outcome; blocked states stay open "
                       "until a receipt closes them"}
    return {"resolved": True, "outcome": claimed_outcome,
            "receipt": outcome_receipt, "absorbing":
                claimed_outcome == "TERMINAL_LOSS"}


def feasibility_attribution(model_capability_isolated: bool,
                            input_coverage_controlled: bool) -> dict:
    """The Manucurist bound: F_prod = f(model, source coverage,
    fidelity threshold, variation cardinality) — multiplicative.
    Blaming the model when input coverage was itself constrained and
    uncontrolled is misattribution: the confounded-confirmation
    family, pointed at AI production failures."""
    if not input_coverage_controlled:
        return {"model_blame_licensed": False,
                "reason": "E_UNCONTROLLED_INPUT_ATTRIBUTION",
                "law": "an AI failure is never automatically the "
                       "model's when quality, volume or coverage of "
                       "the inputs were themselves constrained"}
    return {"model_blame_licensed": model_capability_isolated,
            "note": "with coverage controlled, the model axis is "
                    "separable and may be judged"}


def j4_cursor() -> dict:
    return {"NEXT_TARGET": "J4",
            "J4_MODE": "FAILURES+COUNTEREXAMPLES+NEGATIVE_CONTROLS",
            "expected_gain": "an estimate of where the J3 methods "
                             "stop being valid, not a new method",
            "PROMOTE_TO_CANON": False}
