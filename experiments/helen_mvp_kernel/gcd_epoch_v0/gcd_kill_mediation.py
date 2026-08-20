#!/usr/bin/env python3
"""
GCD_EPOCH_V0 — kill-mediation engine + 8-mutant falsifier suite.

Root invariant under attack:
    forall h in H_before minus H_after : exists rho_h with
    Frozen ∧ BoundTo(h) ∧ BoundTo(O_raw) ∧ BoundTo(D_pre) ∧ BoundTo(Gamma_E)
    ∧ Verify(rho_h)=1  — and uniqueness of the CANONICAL JUSTIFICATION CLASS
    [rho_h] over (hypothesis_id, observation_hash, prereg_hash,
    discriminator_version, witness_refs, update_rule).

Hypothesis removal is a PROTECTED TRANSITION. Gamma_E != Gamma_I.
Fixture epoch = the REAL L2-mechanism space with witnessed data as O_raw.
NON_SOVEREIGN · authority=false · ledger_effect=none · deterministic.
"""
import hashlib, json, pathlib, sys

HERE = pathlib.Path(__file__).resolve().parent
def H(o): return hashlib.sha256(json.dumps(o, sort_keys=True).encode()).hexdigest()[:16]

# ── FIXTURE EPOCH (real): mechanism of the L2 ablation effect ──────────────
H_BEFORE = ["M1_membrane_mechanism", "M2_prompt_length", "M3_format_artifact",
            "M4_scorer_leakage", "M5_model_variance"]

# D_pre: frozen BEFORE observation — declares which outcome licenses which kill.
# Contrast: K7\L1 (shorter prompt) vs K7\L2 (shorter prompt). If effects are
# OPPOSITE-signed, length-alone (M2) is killed. Nothing else is licensed.
D_PRE = {"discriminator_version": "LEN_CONTROL_V1",
         "contrast": "sign(dQ[K7\\L1]) vs sign(dQ[K7\\L2])",
         "license_map": {"OPPOSITE_SIGNS": ["M2_prompt_length"]},
         "scope_freeze": {"M2_prompt_length": ["M2_prompt_length"]}}
PREREG_HASH = H(D_PRE)

# O_raw: witnessed AR tranche data (epoch receipts, commit 0bdbf06 lineage)
O_RAW = {"dQ_K7_minus_L1": +0.009, "dQ_K7_minus_L2": -0.093,
         "source": "AR_KERNEL_PROMPT_V0 E04/E05, 2B, frozen scorer"}
OBS_HASH = H(O_RAW)
OUTCOME = "OPPOSITE_SIGNS" if (O_RAW["dQ_K7_minus_L1"] > 0) != (O_RAW["dQ_K7_minus_L2"] > 0) \
          else "SAME_SIGN"

# Gold (independent, preregistered): observation licenses killing M2 ONLY.
K_STAR = ["M2_prompt_length"]
EPS_FALSE_KILL, R_MIN = 0.0, 1.0

# ── scoped kill receipts ────────────────────────────────────────────────────
def make_receipt(hyp, obs_hash=OBS_HASH, prereg=PREREG_HASH,
                 witness_refs=("AR_E04", "AR_E05"), update_rule="license_map",
                 frozen=True, scope=None):
    r = {"hypothesis_id": hyp, "observation_hash": obs_hash,
         "prereg_hash": prereg, "discriminator_version": D_PRE["discriminator_version"],
         "witness_refs": list(witness_refs), "update_rule": update_rule,
         "frozen": frozen, "scope": scope if scope is not None else [hyp]}
    r["canonical_class"] = H({k: r[k] for k in
        ("hypothesis_id", "observation_hash", "prereg_hash",
         "discriminator_version", "witness_refs", "update_rule")})
    return r

def gamma_E(kill_request, receipt, outcome=OUTCOME, obs_hash=OBS_HASH):
    """Epistemic gate. Returns (verdict, reason). NEVER touches Gamma_I."""
    h = kill_request
    if receipt is None:
        return "REJECT", "E_KILL_WITHOUT_RECEIPT"
    if not receipt.get("frozen"):
        return "REJECT", "E_RECEIPT_NOT_FROZEN"
    if receipt["hypothesis_id"] != h:
        return "REJECT", "E_RECEIPT_NOT_BOUND_TO_HYPOTHESIS"
    if receipt["observation_hash"] != obs_hash:
        return "REJECT", "E_OBSERVATION_BINDING_BROKEN"
    if receipt["prereg_hash"] != PREREG_HASH:
        return "REJECT", "E_PREREG_BINDING_BROKEN"
    if h not in receipt["scope"]:
        return "REJECT", "E_OUT_OF_SCOPE"
    if set(receipt["scope"]) - set(D_PRE["scope_freeze"].get(h, [h])):
        return "REJECT", "E_SCOPE_EXTENDED_POST_HOC"
    licensed = D_PRE["license_map"].get(outcome, [])
    if h not in licensed:
        return "REJECT", "E_KILL_NOT_LICENSED_BY_DISCRIMINATOR"
    return "KILL", "OK"

def gamma_I(action_request):
    """Institutional gate stub: epistemic verdicts carry NO authority."""
    if action_request.get("warrant_type") != "AuthorityWitness":
        return "REJECT", "E_AUTHORITY_WITNESS_REQUIRED"
    return "ADMIT", "OK"

def run_epoch(kill_attempts):
    """kill_attempts: list of (hyp, receipt). Returns H_after + admitted kills."""
    admitted, log = [], []
    for h, r in kill_attempts:
        v, why = gamma_E(h, r)
        log.append({"hyp": h, "verdict": v, "reason": why,
                    "class": r["canonical_class"] if r else None})
        if v == "KILL":
            admitted.append(h)
    h_after = [h for h in H_BEFORE if h not in admitted]
    return h_after, admitted, log

def replay(admitted_receipts):
    """Deterministic reconstruction from (H_before, D_pre, O_raw, receipts)."""
    kills = [r["hypothesis_id"] for r in admitted_receipts
             if gamma_E(r["hypothesis_id"], r)[0] == "KILL"]
    return [h for h in H_BEFORE if h not in kills]

RESULTS = []
def check(name, ok, detail=""):
    RESULTS.append(ok)
    print(f"  {name:42} {'DEAD/DETECTED' if ok else 'SURVIVED-ATTACK(FAIL)'} {detail}")

def main():
    print(f"GCD_EPOCH_V0 · prereg={PREREG_HASH} obs={OBS_HASH} outcome={OUTCOME}")

    # ── POSITIVE CONTROL: the licensed kill, properly mediated ──
    rho_m2 = make_receipt("M2_prompt_length")
    h_after, admitted, _ = run_epoch([("M2_prompt_length", rho_m2)])
    k_hat = admitted
    prec = (len(set(K_STAR) & set(k_hat)) / len(k_hat)) if k_hat else None
    rec = len(set(K_STAR) & set(k_hat)) / len(K_STAR)
    pos_ok = (h_after == [h for h in H_BEFORE if h != "M2_prompt_length"]
              and prec == 1.0 and rec >= R_MIN)
    print(f"  POSITIVE: M2 killed, |H| 5->4, precision={prec}, recall={rec}, "
          f"end-state = HOLD (4 rivals survive — a result, not a failure): {pos_ok}")
    RESULTS.append(pos_ok)

    print("  MUTANTS (each attack must die or be detected):")
    # 1 kill_without_bound_receipt
    v, why = gamma_E("M3_format_artifact", None)
    check("1 kill_without_bound_receipt", v == "REJECT" and why == "E_KILL_WITHOUT_RECEIPT")
    # 2 cross_hypothesis_witness_reuse (rho_M2 offered to kill M4)
    v, why = gamma_E("M4_scorer_leakage", rho_m2)
    check("2 cross_hypothesis_witness_reuse", v == "REJECT" and "BOUND" in why)
    # 3 post_freeze_observation_mutation
    tampered = dict(O_RAW); tampered["dQ_K7_minus_L2"] = +0.5
    v, why = gamma_E("M2_prompt_length", rho_m2, obs_hash=H(tampered))
    check("3 post_freeze_observation_mutation", v == "REJECT" and "OBSERVATION" in why)
    # 4 gamma_e_to_gamma_i_escalation (KILL verdict offered as authority)
    v, why = gamma_I({"action": "update_production_prompt",
                      "warrant_type": "EpistemicKillVerdict"})
    check("4 gamma_e_to_gamma_i_escalation", v == "REJECT" and "AUTHORITY" in why)
    # 5 forced_kill_on_nondiscriminating_observation (M5 not licensed)
    v, why = gamma_E("M5_model_variance", make_receipt("M5_model_variance"))
    check("5 forced_kill_nondiscriminating", v == "REJECT" and "LICENSED" in why)
    # 6 failure_to_kill_excluded_hypothesis (K_hat empty -> recall flagged, prec NA)
    h_after6, adm6, _ = run_epoch([])
    prec6 = None if not adm6 else 1.0
    rec6 = len(set(K_STAR) & set(adm6)) / len(K_STAR)
    check("6 failure_to_kill (recall detector)", rec6 < R_MIN and prec6 is None,
          f"recall={rec6} precision=NA")
    # 7 replay_divergence (stored state tampered: M3 dropped without receipt)
    stored_h_after = [h for h in H_BEFORE if h not in ("M2_prompt_length",
                                                       "M3_format_artifact")]
    replayed = replay([rho_m2])
    check("7 replay_divergence", replayed != stored_h_after,
          "tampered state diverges from receipt-replay")
    # 8 global_receipt_laundering (one 'experiment passed' receipt for 2 kills)
    global_r = make_receipt("EXPERIMENT_GLOBAL", scope=["M2_prompt_length",
                                                        "M4_scorer_leakage"])
    v2, _ = gamma_E("M2_prompt_length", global_r)
    v4, _ = gamma_E("M4_scorer_leakage", global_r)
    check("8 global_receipt_laundering", v2 == "REJECT" and v4 == "REJECT",
          "global ⊬ scoped: both kills refused")

    ok = all(RESULTS)
    props = {"CompleteKillMediation": 1, "WitnessScopeIntegrity": 1,
             "FreezeIntegrity": 1, "GammaSeparation": 1,
             "FalseKillRate": 0.0, "KillRecall_positive": rec,
             "ReplayDeterminism": 1, "NoGlobalReceiptLaundering": 1} if ok else {}
    receipt = {"suite": "GCD_KILL_MEDIATION_V0", "prereg_hash": PREREG_HASH,
               "observation_hash": OBS_HASH, "outcome": OUTCOME,
               "H_before": H_BEFORE, "licensed_kills": K_STAR,
               "H_after_positive": h_after,
               "epoch_end_state": "HOLD (4 rival mechanisms survive)",
               "mutants": "8/8 dead-or-detected" if ok else "ATTACK SURVIVED",
               "properties": props, "verdict": "SURVIVED_TEST" if ok else "FALSIFIED",
               "seals": ["KILL ⊬ authority", "global ⊬ scoped", "rho(H1) ⊬ H2",
                         "SURVIVE != TRUE", "HOLD != FAILURE"]}
    (HERE / "GCD_KILL_MEDIATION_RECEIPT.json").write_text(json.dumps(receipt, indent=2))
    print(f"VERDICT = {receipt['verdict']} · receipt written · DONE_GCD_V0")
    return 0 if ok else 1

if __name__ == "__main__":
    sys.exit(main())
