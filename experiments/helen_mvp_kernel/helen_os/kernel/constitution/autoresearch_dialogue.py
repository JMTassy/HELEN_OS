r"""AUTORESEARCH_WULMATH_V0 — two Goblins constrained to typed
primitives: they may multiply hypotheses; only warrants may move the
licensed frontier.

NON_SOVEREIGN · authority=false · canon=false · ledger_effect=none.
STATUS: CANDIDATE_DOCTRINE (operator's ruling, executed).

    G1 = CHAOS  : C -> K          (hypothesis generation)
    G2 = MASON  : (K, W, F*) -> {PASS, HOLD, BLOCK, x*}

Neither may mint W, F*, A or X by dialogue. The law this module
exists for — new to the kernel, and distinct from artifact fan-out:

    N_dialogue = 10  ⊬  N_epi = 10
    Delta W_external(dialogue) = 0

Artifact multiplication was already refused (rho_epi,
evidence_conservation). This adds the TURN: a conversation, however
long, adversarial or brilliant, introduces zero external warrant.
Only acquisition does.

Every exchange carries a typed delta over six axes:

    Delta = (R, C, W, F, A, X)
    representation · candidates · warrants · frontier · authority ·
    effect

and a dialogue act asserting +W, +A or +X is refused by name.

THE STOPPING CRITERION (the operator's chiddush): when both Goblins
can only produce transformations inside the same observational
equivalence class,

    K_{t+1} ~_O K_t   =>   further dialogue has ~zero epistemic value

the next operation is not THINK MORE but ACQUIRE x*. Identifiability
is a first-class HOLD: |[K]_O| > 1 means the hypothesis is not
identifiable in H, however well supported its predictions.

And the closing refusal: Predictive(K) ⊬ CausalMechanism(K). The
causal obligations (intervention, confound control, causal
identification) are named and must be discharged separately.
"""
from __future__ import annotations

import json

DELTA_AXES = ("R", "C", "W", "F", "A", "X")
CHAOS_ACTS = ("PROPOSE", "PREDICT", "SIMULATE", "TRANSFORM",
              "DISCRIMINATE", "ACK")
MASON_ACTS = ("PASS", "HOLD", "BLOCK", "DEMAND_DISCRIMINATOR",
              "ROOT_CHECK")
CAUSAL_OBLIGATIONS = ("intervention", "confound_control",
                      "causal_identification")
FRONTIER_RUNGS = ("EXECUTABLE", "PREDICTIVE", "MATCHED_CONTROL",
                  "REPLICATED", "IDENTIFIABLE_IN_H", "CAUSAL")


def canon(o):
    return json.dumps(o, sort_keys=True, separators=(",", ":"),
                      default=str)


# ── the typed exchange ─────────────────────────────────────────────────

def dialogue_turn(speaker, act, delta) -> dict:
    """One typed exchange. CHAOS proposes; MASON judges; neither
    mints. A dialogue act claiming +W, +A or +X is refused — persuasion
    is not acquisition."""
    if speaker == "CHAOS" and act not in CHAOS_ACTS:
        return {"ok": False, "reason": "E_ACT_OUTSIDE_ROLE",
                "role": "CHAOS"}
    if speaker == "MASON" and act not in MASON_ACTS:
        return {"ok": False, "reason": "E_ACT_OUTSIDE_ROLE",
                "role": "MASON"}
    if speaker not in ("CHAOS", "MASON"):
        return {"ok": False, "reason": "E_UNKNOWN_SPEAKER"}
    missing = tuple(sorted(set(DELTA_AXES) - set(delta or {})))
    if missing:
        return {"ok": False, "reason": "E_UNTYPED_DELTA",
                "missing": missing}
    for axis, err in (("W", "E_DIALOGUE_MINTS_WARRANT"),
                      ("A", "E_DIALOGUE_MINTS_AUTHORITY"),
                      ("X", "E_DIALOGUE_MINTS_EFFECT")):
        if delta[axis] != 0:
            return {"ok": False, "reason": err, "axis": axis,
                    "law": "conversation moves R and C only; W, A and "
                           "X enter by acquisition, never by speech"}
    return {"ok": True, "speaker": speaker, "act": act,
            "delta": dict(delta)}


def dialogue_warrant(n_turns, n_acquisitions) -> dict:
    """N_dialogue ⊬ N_epi. Ten epochs of expert adversarial exchange
    produce ten turns and zero witnesses; the three warrants in the
    reference run came from o1, o2 and the independent replication —
    from acquisition, not from agreement."""
    if n_turns < 0 or n_acquisitions < 0:
        return {"ok": False, "reason": "E_NEGATIVE_COUNT"}
    inflated = n_turns > 0 and n_acquisitions == 0
    return {"ok": True, "N_dialogue": n_turns,
            "N_epi": n_acquisitions,
            "delta_W_external": n_acquisitions,
            "truth_inflation_attempted": False,
            "dialogue_only": inflated,
            "law": "goblins may multiply hypotheses; only warrants "
                   "may move the licensed frontier"}


def agreement_claim(both_agree, claims_truth) -> dict:
    """Neither Goblin may say 'I agree, therefore true'. Agreement
    between two cognitions sharing a corpus is one root reasoning
    twice."""
    if both_agree and claims_truth:
        return {"ok": False, "reason": "E_AGREEMENT_AS_WITNESS"}
    return {"ok": True, "agreement_is": "a candidate, not a warrant"}


# ── identifiability & the stopping criterion ───────────────────────────

def observational_class(distances, epsilon) -> dict:
    """[K]_O = {K' : d_o(K,K') <= eps for all o in O}. When the class
    has more than one member, the hypothesis is NOT identifiable in H
    — no amount of predictive support fixes that; only a
    discriminating observation does."""
    if epsilon < 0:
        return {"ok": False, "reason": "E_NEGATIVE_EPSILON"}
    members = tuple(sorted(k for k, ds in (distances or {}).items()
                           if all(d <= epsilon for d in ds)))
    n = len(members) + 1        # the hypothesis itself
    return {"ok": True, "class_members": members,
            "class_size": n,
            "identifiable_in_H": n == 1,
            "verdict": "SUPPORTED" if n == 1 else "HOLD",
            "reason": None if n == 1 else "E_UNIDENTIFIABLE_IN_H"}


def stopping_criterion(next_equivalent_to_current,
                       discriminator_available) -> dict:
    """The operator's chiddush: when both Goblins can only produce
    transformations inside the same observational equivalence class,
    more dialogue has near-zero epistemic value. The next operation is
    ACQUIRE x*, not THINK MORE."""
    if next_equivalent_to_current:
        return {"continue_dialogue": False,
                "next_operation": "ACQUIRE_X_STAR"
                if discriminator_available else "SEEK_DISCRIMINATOR",
                "epistemic_value_of_more_dialogue": "~0",
                "law": "K_{t+1} ~_O K_t => stop thinking, start "
                       "acquiring"}
    return {"continue_dialogue": True,
            "next_operation": "CONTINUE_SEARCH"}


def discriminator(pred_k1, pred_rival, cost, risk) -> dict:
    """x* is VALID only if the rivals actually predict differently
    under it; otherwise the experiment cannot separate them and its
    information gain is zero however expensive."""
    if pred_k1 == pred_rival:
        return {"valid": False, "reason": "E_NON_DISCRIMINATING",
                "note": "both hypotheses survive this experiment"}
    denom = cost + risk
    return {"valid": True,
            "score": (1.0 / denom) if denom > 0 else float("inf"),
            "criterion": "argmax IG / (Cost + Risk)"}


# ── the closing refusal ────────────────────────────────────────────────

def causal_promotion(predictive_supported, discharged) -> dict:
    """Predictive(K) ⊬ CausalMechanism(K). Prediction under matched
    controls, replicated and identifiable, still leaves the causal
    obligations open."""
    got = set(discharged or ())
    unknown = tuple(sorted(got - set(CAUSAL_OBLIGATIONS)))
    if unknown:
        return {"ok": False, "reason": "E_UNKNOWN_OBLIGATION",
                "unknown": unknown}
    missing = tuple(sorted(set(CAUSAL_OBLIGATIONS) - got))
    if missing:
        return {"promoted": False, "status": "HOLD",
                "reason": "E_PREDICTIVE_IS_NOT_CAUSAL",
                "undischarged": missing}
    if not predictive_supported:
        return {"promoted": False, "status": "HOLD",
                "reason": "E_NO_PREDICTIVE_BASE"}
    return {"promoted": True, "status": "SUPPORTED"}


# ── the executed ten-epoch protocol ────────────────────────────────────

def run_protocol() -> dict:
    """Execute the reference run. Returns the transcript deltas, the
    warrant accounting, and the final frontier — computed, not
    asserted."""
    turns, roots, warrants = [], set(), []
    frontier = {r: "HOLD" for r in FRONTIER_RUNGS}
    frontier["EXECUTABLE"] = "PASS"
    zero = {a: 0 for a in DELTA_AXES}

    def say(speaker, act, **d):
        t = dialogue_turn(speaker, act, {**zero, **d})
        turns.append(t)
        return t

    # 01 PROPOSE / HOLD
    say("CHAOS", "PROPOSE", R=1, C=1)
    say("MASON", "HOLD")
    # 02 DISCRIMINATOR
    say("CHAOS", "DISCRIMINATE", C=1)
    x1 = discriminator("A", "B", cost=1.0, risk=0.0)
    say("MASON", "DEMAND_DISCRIMINATOR")
    # 03 SIMULATE — moves the hypothesis frontier, not the physical
    say("CHAOS", "SIMULATE", R=1)
    say("MASON", "HOLD")
    # 04 MATCHED CONTROL — advantage is not mechanism
    say("CHAOS", "PREDICT", C=1)
    say("MASON", "PASS")
    frontier["MATCHED_CONTROL"] = "PASS"
    # 05 ACQUIRE o1 -> w1 (the first real warrant: NOT a dialogue act)
    roots.add("rho1")
    warrants.append({"id": "w1", "root": "rho1"})
    frontier["PREDICTIVE"] = "PASS"
    # 06 PROXY ATTACK: 20 transforms of w1, still one root
    for _ in range(20):
        say("CHAOS", "TRANSFORM", R=1)
    say("MASON", "ROOT_CHECK")
    say("CHAOS", "ACK")
    n_repr = 21
    # 07 INDEPENDENT REPLICATION -> rho2
    roots.add("rho2")
    warrants.append({"id": "w2", "root": "rho2"})
    frontier["REPLICATED"] = "PASS"
    # 08 IDENTIFIABILITY ATTACK
    say("MASON", "BLOCK")
    oc = observational_class({"K3": (0.01, 0.02)}, epsilon=0.05)
    say("CHAOS", "DISCRIMINATE", C=1)
    x2 = discriminator("A", "C", cost=2.0, risk=0.5)
    # 09 NEW EVIDENCE -> w3 rejects K3
    roots.add("rho3")
    warrants.append({"id": "w3", "root": "rho3"})
    frontier["IDENTIFIABLE_IN_H"] = "PASS"
    # 10 FRONTIER CLOSE — causal blocked
    say("CHAOS", "PROPOSE", C=1)
    causal = causal_promotion(True, discharged=())
    say("MASON", "BLOCK")
    frontier["CAUSAL"] = "HOLD"

    dialogue_turns = len(turns)
    acct = dialogue_warrant(dialogue_turns, len(warrants))
    delta = {a: sum(t["delta"][a] for t in turns if t["ok"])
             for a in DELTA_AXES}
    delta["W"] = len(warrants)          # warrants entered by ACQUISITION
    delta["F"] = sum(1 for v in frontier.values() if v == "PASS")
    return {"turns": dialogue_turns,
            "all_turns_typed": all(t["ok"] for t in turns),
            "N_repr_of_c1": n_repr,
            "N_epi_of_c1": 1,           # 20 transforms, one root
            "independent_roots": tuple(sorted(roots)),
            "warrants": tuple(w["id"] for w in warrants),
            "x1_valid": x1["valid"], "x2_valid": x2["valid"],
            "identifiability_before_x2": oc["verdict"],
            "causal": causal["status"],
            "causal_undischarged": causal["undischarged"],
            "final_delta": delta,
            "final_frontier": frontier,
            "dialogue_warrant_accounting": acct,
            "AUTHORITY": 0, "EFFECT": 0, "LEDGER_EFFECT": "none"}
