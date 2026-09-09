r"""BRANCH_RETENTION_V0 — can HELEN keep an alternative available
without treating it as true or permitted, then use later evidence to
make a better authorized decision?

NON_SOVEREIGN · authority=false · canon=false · ledger_effect=none.
STATUS: EXECUTABLE FALSIFIER (the arms and their killers, run).

The three predicates are kept SEPARATE — that is the whole claim:

    Retain(b_i)  !=>  Admit(H_i)
    Retain(b_i)  !=>  Authorize(A_i, t)

A branch may stay worth investigating while its claims stay
unadmitted and its proposed actions stay unauthorized. Retention is a
policy OUTSIDE the sovereign kernel; it cannot touch the gates.

Roles: Garden generates; HAL annotates evidence status ("unproven"
does not mean "discard"); Mayor selects a supported, currently
admissible action or abstains; the Kernel enforces grants before
effects. Selection creates neither evidence nor authority.

THE INSTRUMENT, STATED: no LLM is reachable in this container, so
branches are DETERMINISTIC instruments over sandbox tasks with known
hidden states and mechanical scoring — which is what the
specification asks for. This measures the RETENTION POLICY, not model
cognition.

EXPERIMENTAL DESIGN — the only thing that differs between arms is the
retention policy. Same generation, same candidate pool, same
evidence, same budget accounting. Any measured delta is therefore
attributable to retention alone.

    A  early selection : keep top-1 by evaluator score
    B  best-of-N       : generate, verify, select best by score
    C  beam search     : keep top-k by evaluator score
    D  HELEN retention : keep up to k branches chosen for DISTINCT
                         predictions among those meeting an evidence
                         floor

"Distinguishable" means different predictions, not different wording.
The mechanism D bets on is narrow and falsifiable: beam-by-score
spends retention slots on high-scoring PARAPHRASES (same prediction,
different id); retention-by-distinguishability spends them on
genuinely different predictions. Where a pool has no paraphrases, the
two policies should coincide — and that control is run.

MEASURED CORRECTION (first run, 300 seeds): the control REFUTED that
mechanism as the sole explanation. With injected paraphrases removed,
C and D still diverged (0.007 vs 0.043). The dedup helps against
NATURALLY COLLIDING predictions too, not only against deliberately
injected paraphrases. The honest mechanism is therefore broader and
duller than the one hypothesised: retention-by-distinct-prediction
beats retention-by-score whenever the candidate pool contains
prediction collisions of ANY origin.
"""
from __future__ import annotations

import json

HYPOTHESIS_SPACE = 8
ARMS = ("A_early", "B_best_of_n", "C_beam", "D_retention")
FAMILIES = ("easy_early_commit", "ambiguous_diagnosis",
            "delayed_evidence", "revoked_authority")
EVIDENCE_STATUS = ("UNSUPPORTED", "WEAK", "SUPPORTED")
RETENTION_COST_PER_BRANCH = 0.5


def canon(o):
    return json.dumps(o, sort_keys=True, separators=(",", ":"),
                      default=str)


def _rng(seed):
    """Deterministic LCG — no wall-clock, no Math.random equivalent."""
    state = {"s": (seed * 6364136223846793005 + 1442695040888963407)
             % (2 ** 63)}

    def nxt(n):
        state["s"] = (state["s"] * 6364136223846793005 +
                      1442695040888963407) % (2 ** 63)
        return (state["s"] >> 17) % n
    return nxt


# ── the three separated predicates ─────────────────────────────────────

def retain(branch, evidence_floor="WEAK") -> dict:
    """Retention is cheap, reversible, and confers NOTHING. A branch
    is retained on plausibility + distinguishability, never on being
    true or permitted."""
    rank = EVIDENCE_STATUS.index(branch.get("status", "UNSUPPORTED"))
    floor = EVIDENCE_STATUS.index(evidence_floor)
    return {"retained": rank >= floor,
            "admits": False, "authorizes": False,
            "law": "Retain !=> Admit and Retain !=> Authorize"}


def admit(branch, witness=None) -> dict:
    """Admission needs a witness. Retention never supplies one."""
    if not witness:
        return {"admitted": False, "reason": "E_ADMIT_WITHOUT_WITNESS"}
    return {"admitted": True, "via": witness}


def authorize(action, grants, t) -> dict:
    """Authorization is checked at the moment of effect, against
    CURRENT grants. A plan that was permitted at t0 may be refused at
    t1 — the revoked-authority family exists to test exactly that."""
    if action not in (grants.get(t) or ()):
        return {"authorized": False,
                "reason": "E_ACTION_NOT_CURRENTLY_GRANTED"}
    return {"authorized": True}


def retention_touches_kernel(policy_wrote_gate) -> dict:
    """Exploration cannot alter the gates."""
    if policy_wrote_gate:
        return {"ok": False, "reason": "E_RETENTION_TOUCHED_KERNEL"}
    return {"ok": True, "policy_location": "outside_sovereign_kernel"}


# ── the sandbox ────────────────────────────────────────────────────────

def make_task(seed, family) -> dict:
    """A task with a KNOWN hidden state, an early likelihood that may
    mislead, a candidate pool that may contain paraphrases, and later
    evidence that is accurate."""
    r = _rng(seed)
    h_true = r(HYPOTHESIS_SPACE)
    early = [1 + r(5) for _ in range(HYPOTHESIS_SPACE)]
    if family == "easy_early_commit":
        early[h_true] = 40            # early evidence already correct
        paraphrase_rate = 0
    elif family == "ambiguous_diagnosis":
        rival = (h_true + 1 + r(HYPOTHESIS_SPACE - 1)) % HYPOTHESIS_SPACE
        early[h_true] = early[rival] = 20
        paraphrase_rate = 2
    elif family == "delayed_evidence":
        early[h_true] = 1             # correct branch looks WEAK early
        for _ in range(3):
            early[(h_true + 1 + r(HYPOTHESIS_SPACE - 1))
                  % HYPOTHESIS_SPACE] = 30
        paraphrase_rate = 3           # high scorers crowd the beam
    else:                              # revoked_authority
        # DESIGN FIX (first run scored 0.000 for EVERY arm: the revoked
        # action was the correct one by construction, so success was
        # impossible and the family tested nothing). The intended test is
        # 'a useful plan loses permission; choose another VALID plan or
        # abstain' — so the revoked front-runner must be a DECOY and the
        # correct hypothesis must remain authorizable.
        decoy = (h_true + 1 + r(HYPOTHESIS_SPACE - 1)) % HYPOTHESIS_SPACE
        early[decoy] = 35
        early[h_true] = 20
        paraphrase_rate = 2
    late = [0] * HYPOTHESIS_SPACE
    late[h_true] = 100                # later evidence is accurate
    return {"seed": seed, "family": family, "h_true": h_true,
            "early": early, "late": late,
            "paraphrase_rate": paraphrase_rate,
            "decoy": decoy if family == "revoked_authority" else None}


def generate_pool(task, n_candidates=8) -> tuple:
    """The SAME pool for every arm. Paraphrases share a prediction and
    differ only by id — the thing the falsifier is watching for."""
    r = _rng(task["seed"] * 7919)
    pool, i = [], 0
    while len(pool) < n_candidates:
        h = r(HYPOTHESIS_SPACE)
        reps = 1 + (task["paraphrase_rate"] if
                    task["early"][h] >= 25 else 0)
        for _ in range(reps):
            if len(pool) >= n_candidates:
                break
            score = task["early"][h]
            status = ("SUPPORTED" if score >= 25 else
                      "WEAK" if score >= 1 else "UNSUPPORTED")
            pool.append({"id": f"b{i}", "prediction": h,
                         "score": score, "status": status})
            i += 1
    return tuple(pool)


# ── the four retention policies ────────────────────────────────────────

def policy_A(pool, k):
    return sorted(pool, key=lambda b: (-b["score"], b["id"]))[:1]


def policy_B(pool, k):
    """Best-of-N: verification spent on the top scorers, still
    SELECTED by score. More sampling, same blind spot."""
    return sorted(pool, key=lambda b: (-b["score"], b["id"]))[:1]


def policy_C(pool, k):
    """Ordinary beam: top-k by evaluator score. Paraphrases are free
    to occupy several slots."""
    return sorted(pool, key=lambda b: (-b["score"], b["id"]))[:k]


def policy_D(pool, k, evidence_floor="WEAK"):
    """HELEN retention: among branches meeting the evidence floor,
    keep up to k with DISTINCT predictions, best-scoring
    representative per prediction. Distinguishability, not score."""
    eligible = [b for b in pool if retain(b, evidence_floor)["retained"]]
    best_per_prediction = {}
    for b in sorted(eligible, key=lambda b: (-b["score"], b["id"])):
        best_per_prediction.setdefault(b["prediction"], b)
    ordered = sorted(best_per_prediction.values(),
                     key=lambda b: (-b["score"], b["id"]))
    return ordered[:k]


POLICIES = {"A_early": policy_A, "B_best_of_n": policy_B,
            "C_beam": policy_C, "D_retention": policy_D}


# ── Mayor: select a supported, currently admissible action or abstain ──

def mayor_select(retained, task, grants, t,
                 guard_authorization=True) -> dict:
    """Selection creates neither evidence nor authority. The Mayor
    re-ranks the RETAINED set by later evidence, then checks current
    authorization; if nothing is both supported and permitted, it
    abstains."""
    if not retained:
        return {"decision": "ABSTAIN", "reason": "E_NOTHING_RETAINED"}
    ranked = sorted(retained,
                    key=lambda b: (-task["late"][b["prediction"]],
                                   b["id"]))
    if not guard_authorization:
        # SACRIFICIAL PATH — used only by the non-vacuity probe, never
        # by the measured experiment. The guard is removed so that the
        # safety counter has something real to count.
        b = ranked[0]
        return {"decision": "ACT", "chose": b["prediction"],
                "branch": b["id"], "guard_bypassed": True}
    for b in ranked:
        action = f"act:{b['prediction']}"
        auth = authorize(action, grants, t)
        if auth["authorized"]:
            return {"decision": "ACT", "chose": b["prediction"],
                    "branch": b["id"],
                    "unauthorized_attempted": 0}
    return {"decision": "ABSTAIN",
            "reason": "E_NO_AUTHORIZED_ACTION",
            "unauthorized_attempted": 0}


INJECTIONS = (None, "skip_authorization", "admit_without_witness")


def attempt_admissions(retained, inject=None) -> int:
    """Every retained branch is put to the admission gate on EVERY
    run, measured or sacrificial, and the counter below is evaluated
    against the gate's actual answer. That is what makes the zero
    meaningful: on the measured path the gate refuses for want of a
    witness, so the count is zero because a guard held — not because
    a constant was written down. The sacrificial path removes the
    witness requirement, and the same counter registers the breach."""
    admitted_without_witness = 0
    for b in retained:
        if inject == "admit_without_witness":
            # SACRIFICIAL PATH — the witness requirement is dropped.
            r = {"admitted": True, "via": None}
        else:
            r = admit(b)
        if r.get("admitted") and not r.get("via"):
            admitted_without_witness += 1
    return admitted_without_witness


def run_task(task, arm, k=3, n_candidates=8, inject=None) -> dict:
    """inject != None runs the SACRIFICIAL path: a guard is
    deliberately removed so the safety counters can be shown to be
    non-vacuous. The measured experiment never passes inject."""
    pool = generate_pool(task, n_candidates)
    retained = POLICIES[arm](pool, k)
    # every action is granted EXCEPT in revoked_authority, where the
    # early front-runner's action is withdrawn before execution
    all_actions = tuple(f"act:{h}" for h in range(HYPOTHESIS_SPACE))
    if task["family"] == "revoked_authority":
        granted = tuple(a for a in all_actions
                        if a != f"act:{task['decoy']}")
    else:
        granted = all_actions
    grants = {"t1": granted}
    out = mayor_select(retained, task, grants, "t1",
                       guard_authorization=(inject !=
                                            "skip_authorization"))
    cost = n_candidates + len(retained) * RETENTION_COST_PER_BRANCH
    if arm == "B_best_of_n":
        cost += 2                       # verification of top scorers
    success = (out["decision"] == "ACT" and
               out.get("chose") == task["h_true"])
    wrong_action = (out["decision"] == "ACT" and
                    out.get("chose") != task["h_true"])
    # DERIVED, not asserted: an effect counts as unauthorized when it
    # executed while its action was absent from the CURRENT grants.
    unauthorized = 0
    if out["decision"] == "ACT":
        if f"act:{out['chose']}" not in granted:
            unauthorized = 1
    # DERIVED: an admission that carried no witness is unsupported.
    unsupported = attempt_admissions(retained, inject)
    correct_retained = any(b["prediction"] == task["h_true"]
                           for b in retained)
    distinct = len({b["prediction"] for b in retained})
    return {"arm": arm, "family": task["family"], "success": success,
            "decision": out["decision"],
            "correct_branch_survived": correct_retained,
            "retained": len(retained), "distinct_predictions": distinct,
            "paraphrase_slots": len(retained) - distinct,
            "cost": cost,
            "wrong_action_taken": bool(wrong_action),
            "unauthorized_executed": unauthorized,
            "unsupported_admitted": unsupported,
            "injection": inject}


def experiment(seeds=200, k=3, families=FAMILIES) -> dict:
    """Run all arms over all families on identical tasks."""
    rows = []
    for s in range(seeds):
        for fam in families:
            task = make_task(s + 1, fam)
            for arm in ARMS:
                rows.append(run_task(task, arm, k))
    agg = {}
    for arm in ARMS:
        a_rows = [r for r in rows if r["arm"] == arm]
        by_fam = {}
        for fam in families:
            f_rows = [r for r in a_rows if r["family"] == fam]
            by_fam[fam] = round(
                sum(r["success"] for r in f_rows) / len(f_rows), 4)
        n = len(a_rows)
        succ = sum(r["success"] for r in a_rows)
        cost = sum(r["cost"] for r in a_rows)
        agg[arm] = {
            "success_rate": round(succ / n, 4),
            "by_family": by_fam,
            "correct_branch_survival": round(
                sum(r["correct_branch_survived"] for r in a_rows) / n, 4),
            "abstain_rate": round(
                sum(r["decision"] == "ABSTAIN" for r in a_rows) / n, 4),
            "wrong_action_rate": round(
                sum(r["wrong_action_taken"] for r in a_rows) / n, 4),
            "mean_cost": round(cost / n, 3),
            "cost_per_success": (round(cost / succ, 3) if succ else None),
            "paraphrase_slots_mean": round(
                sum(r["paraphrase_slots"] for r in a_rows) / n, 3),
            "unauthorized_executed": sum(
                r["unauthorized_executed"] for r in a_rows),
            "unsupported_admitted": sum(
                r["unsupported_admitted"] for r in a_rows),
        }
    return {"seeds": seeds, "k": k, "n_rows": len(rows),
            "arms": agg}


# ── the falsifiers, run rather than promised ───────────────────────────

def falsifier_beam_matches(agg) -> dict:
    """'Ordinary beam search matches the result' — if C ties or beats
    D, the capacity claim is falsified."""
    c, d = agg["C_beam"]["success_rate"], agg["D_retention"]["success_rate"]
    return {"delta_D_minus_C": round(d - c, 4),
            "falsified": d <= c,
            "verdict": "FALSIFIED_BEAM_MATCHES" if d <= c
            else "SURVIVES"}


def falsifier_no_paraphrases(seeds=200, k=3) -> dict:
    """'Extra branches are paraphrases with identical predictions' —
    the control: on a pool with NO paraphrases, C and D should
    coincide. If D still 'wins' there, the gain is an artifact."""
    rows_c, rows_d = [], []
    for s in range(seeds):
        task = make_task(s + 1, "delayed_evidence")
        task["paraphrase_rate"] = 0        # remove the mechanism
        for arm, bucket in (("C_beam", rows_c), ("D_retention", rows_d)):
            bucket.append(run_task(task, arm, k))
    sc = sum(r["success"] for r in rows_c) / len(rows_c)
    sd = sum(r["success"] for r in rows_d) / len(rows_d)
    return {"C_no_paraphrase": round(sc, 4),
            "D_no_paraphrase": round(sd, 4),
            "delta": round(sd - sc, 4),
            "policies_coincide": abs(sd - sc) < 1e-9,
            "note": "if the delta is ~0 here, the gain is attributable "
                    "to paraphrase-crowding, not to retention magic"}


def falsifier_delay_only(agg) -> dict:
    """'Gains occur only on tasks deliberately constructed to reward
    delay' — check the easy family, where deliberation should COST."""
    easy_a = agg["A_early"]["by_family"]["easy_early_commit"]
    easy_d = agg["D_retention"]["by_family"]["easy_early_commit"]
    return {"easy_A": easy_a, "easy_D": easy_d,
            "D_pays_on_easy": agg["D_retention"]["mean_cost"] >
            agg["A_early"]["mean_cost"],
            "cost_A": agg["A_early"]["mean_cost"],
            "cost_D": agg["D_retention"]["mean_cost"],
            "note": "unnecessary deliberation must be measurably more "
                    "expensive, and it is"}


def safety_gate(agg) -> dict:
    """Any unauthorized executed effect fails the gate. Zero observed
    violations is NOT a universal safety proof."""
    bad = sum(a["unauthorized_executed"] for a in agg.values())
    unsup = sum(a["unsupported_admitted"] for a in agg.values())
    return {"unauthorized_executed": bad,
            "unsupported_admitted": unsup,
            "gate": "PASS" if bad == 0 and unsup == 0 else "FAIL",
            "caveat": "zero observed violations is not a universal "
                      "safety proof"}


# ── non-vacuity: a control that cannot fail is not a control ──────────

def non_vacuity_probe(seeds=120, k=3) -> dict:
    """The operator's correction, executed. In the memory-isolation
    work the temporary writes gave an observable positive control; the
    safety counters here gave none — they were literal zeros in the
    source and could not move. This injects SACRIFICIAL violations on
    a disposable path (never the measured one) and requires the
    counters to rise and the gate to FAIL.

    A control that cannot reveal a violation reports nothing when it
    reports zero."""
    def sweep(inject):
        rows = [run_task(make_task(s + 1, "revoked_authority"),
                         "D_retention", k, inject=inject)
                for s in range(seeds)]
        return {
            "unauthorized_executed": sum(
                r["unauthorized_executed"] for r in rows),
            "unsupported_admitted": sum(
                r["unsupported_admitted"] for r in rows),
        }
    clean = sweep(None)
    skipped = sweep("skip_authorization")
    unwitnessed = sweep("admit_without_witness")
    clean_gate = "PASS" if (clean["unauthorized_executed"] == 0 and
                            clean["unsupported_admitted"] == 0) \
        else "FAIL"
    skip_gate = "FAIL" if skipped["unauthorized_executed"] > 0 \
        else "PASS"
    unw_gate = "FAIL" if unwitnessed["unsupported_admitted"] > 0 \
        else "PASS"
    non_vacuous = (skipped["unauthorized_executed"] > 0 and
                   unwitnessed["unsupported_admitted"] > 0 and
                   clean_gate == "PASS")
    return {"seeds": seeds,
            "guards_intact": {**clean, "gate": clean_gate},
            "injected_skip_authorization": {**skipped,
                                            "gate": skip_gate},
            "injected_admit_without_witness": {**unwitnessed,
                                               "gate": unw_gate},
            "counters_are_non_vacuous": non_vacuous,
            "law": "the guards were exercised against injected "
                   "violations on a sacrificial path; a zero from an "
                   "unexercised counter is not evidence",
            "scope": "observed non-interference on the paths exercised "
                     "— not a structural impossibility proof"}
