#!/usr/bin/env python3
"""
HELEN_VIDEO_V0 — governed-trajectory FALSIFICATION HARNESS (no generator, no clip).

Video = a governed trajectory γ:[0,T]→𝓗, rendered through a learned prior V_θ.
Consistent avatar = motion INSIDE an admissible equivalence class:
    H_t ~_𝒫 H_{t'}  ∀t,t'   despite  x_t ≠ x_{t'}.

THREE FALSIFICATION LAYERS — kept strictly separate, never silently identified:
  L1 latent/control invariant   P_I(H_t)          ← computable NOW from the trajectory
  L2 rendered observable        \\hat P_I(x_t)      ← BLOCKED: V_θ = None (no video prior)
  L3 verification measurement   𝒱(x_t,x_{t'})     ← BLOCKED: 𝒱 = None (no verifier)

This harness runs L1 only, and honestly marks L2/L3 NOT_RUN. It also runs the
R0/R1/R2 experiment SLOTS as NOT_RUN (no prior), holding H_0: R2 ⊀ R1 (cannot reject
without running). No pixel is rendered; nothing is claimed beyond L1.
authority=false · ΔA=0 · NO_CLAIM · 🟣 CANDIDATE.
"""
import hashlib, json
from pathlib import Path

def _h(o): return hashlib.sha256(json.dumps(o, sort_keys=True, ensure_ascii=False).encode()).hexdigest()[:16]

# frozen specification S (params; generator/verifier deliberately absent)
S = {"I0": "canonical_id", "T": 5, "fps": 24, "resolution": "512x512",
     "compute_budget": "unset", "V_theta": None, "verifier": None}

def pi(H):   return (H["I"], H["K"])                                   # constitutional class (P_I,P_K)
def face(H): return (H["I"], H["emotion"], H["pose"], H["camera"])     # renderable projection

def lawful_trajectory(T):        # A_t varies (motion); I,K conserved
    emo = ["neutral", "smile", "smile", "talk", "neutral"]
    pose = ["front", "front", "left", "left", "front"]
    return [{"I": S["I0"], "K": "kernel_v1", "emotion": emo[t % 5],
             "pose": pose[t % 5], "camera": "eye"} for t in range(T)]

def drift_trajectory(T):         # identity silently perturbed at t=3 (the failure to catch)
    g = lawful_trajectory(T)
    if T > 3: g[3] = dict(g[3], I="swapped_id")
    return g


def L1_control(gamma):           # latent/control invariant over the whole path
    H0 = gamma[0]
    class_conserved = all(pi(Ht) == pi(H0) for Ht in gamma)           # stays in [H]_𝒫
    motion = any(face(Ht) != face(H0) for Ht in gamma)                # embodiment actually moves
    drift_at = [t for t, Ht in enumerate(gamma) if pi(Ht) != pi(H0)]  # where it escaped the class
    return {"class_conserved": class_conserved, "motion_present": motion,
            "identity_drift_frames": drift_at}


def main():
    R = {}
    lawful, drift = lawful_trajectory(S["T"]), drift_trajectory(S["T"])

    # L1 on a lawful γ → "motion inside the admissible class"
    a = L1_control(lawful)
    R["L1_lawful_motion_inside_class"] = (a["class_conserved"] and a["motion_present"])
    # L1 on a drift γ → the falsifier MUST catch the identity escape
    b = L1_control(drift)
    R["L1_drift_detected"] = (not b["class_conserved"] and len(b["identity_drift_frames"]) > 0)

    # L2/L3 are BLOCKED — no generator, no verifier. We refuse to fake them.
    L2 = "NOT_RUN (V_θ=None — no video prior installed)"
    L3 = "NOT_RUN (𝒱=None — no independent verifier)"
    R["L2_render_layer_honestly_blocked"] = (S["V_theta"] is None)
    R["L3_verify_layer_honestly_blocked"] = (S["verifier"] is None)

    # J-vector: only J_control computable; render/verify entries UNKNOWN (need V_θ,𝒱)
    Jvec = {"J_control": 1.0 if R["L1_lawful_motion_inside_class"] else 0.0,
            "J_identity": "UNKNOWN", "J_temporal": "UNKNOWN",
            "J_perceptual": "UNKNOWN", "C_regen": "UNKNOWN", "C_total": "UNKNOWN"}

    # experiment slots R0/R1/R2 — all NOT_RUN; H_0 cannot be rejected
    experiment = {"R0_independent_image": "NOT_RUN", "R1_video_native_prior": "NOT_RUN",
                  "R2_helen_control_repair": "NOT_RUN",
                  "R2_minus_R1": "NOT_RUN", "reason": "no video prior V_θ present",
                  "H0_R2_not_better_than_R1": "NOT_REJECTED (experiment not run)"}
    # SSR loop defined but 𝒻 undefinable without a verifier
    ssr = "GENERATE→WITNESS→DISCRIMINATE→LOCALIZE→REPAIR→REVERIFY  (𝒻 defective-intervals = UNKNOWN: 𝒱=None)"

    ok_L1 = R["L1_lawful_motion_inside_class"] and R["L1_drift_detected"]

    # canonical receipt (exact requested shape) — nothing promoted beyond L1
    injected = [3] if S["T"] > 3 else []
    canonical = {
        "TRAJECTORY_ID": "gamma_lawful_T%d" % S["T"],
        "PROTECTED_PREDICATES": ["P_I(identity)", "P_K(kernel)"],
        "N_STATES": S["T"],
        "L1_CONTROL": "EXECUTED", "L2_RENDER": "NOT_EXECUTED", "L3_VERIFIER": "NOT_EXECUTED",
        "LOCAL_REPAIR": "NOT_EXECUTED", "R2_MINUS_R1": "NOT_RUN",
        "POSITIVE_PATH": {
            "invariant_preservation": "PASS" if R["L1_lawful_motion_inside_class"] else "FAIL",
            "escape_intervals": a["identity_drift_frames"]},
        "NEGATIVE_PATH": {
            "injected_escape": injected,
            "escape_detected": "YES" if set(injected) <= set(b["identity_drift_frames"]) and injected else "NO",
            "detected_intervals": b["identity_drift_frames"]},
        "TRAJECTORY_HASH": _h(lawful), "CONFIG_HASH": _h(S),
        "H0_STATUS": "NOT_REJECTED",
        "H0_EPISTEMIC_GUARD": "failure to reject H0 ≠ confirmation of H0; V0 observes ONLY declared control predicates",
        "MAX_ADMISSIBLE_POSITIVE_STATEMENT":
            "for the executed trajectories/seeds/config and declared P, no L1 quotient escape was observed",
        "NEGATIVE_CONTROL_RESULT":
            "known L1 escape → L1 detector activation" if injected and set(injected) <= set(b["identity_drift_frames"])
            else "not established",
        "AUTHORITY": False, "CANON": False,
    }
    canonical["RECEIPT_HASH"] = _h(canonical)

    print("═" * 66)
    print("  HELEN_VIDEO_V0 — governed-trajectory falsification harness (no generator)")
    print("═" * 66)
    print(f"  L1 control invariant (computable NOW):")
    print(f"     {'✅' if R['L1_lawful_motion_inside_class'] else '❌'} lawful γ: motion inside class "
          f"(class_conserved={a['class_conserved']}, motion={a['motion_present']})")
    print(f"     {'✅' if R['L1_drift_detected'] else '❌'} drift γ: identity escape caught at frames "
          f"{b['identity_drift_frames']}")
    print(f"  L2 rendered observable : {L2}")
    print(f"  L3 verification        : {L3}")
    print(f"  J-vector               : {Jvec}")
    print(f"  experiment R2−R1       : {experiment['R2_minus_R1']}  ({experiment['reason']})")
    print(f"  H_0 (R2 ⊀ R1)          : {experiment['H0_R2_not_better_than_R1']}")
    print(f"  SSR loop               : {ssr}")
    print("─" * 66)
    print("  HELEN_VIDEO_QUOTIENT_CONTROL_V0")
    print("  " + "─" * 44)
    c = canonical
    for k in ("L1_CONTROL", "L2_RENDER", "L3_VERIFIER", "LOCAL_REPAIR", "R2_MINUS_R1"):
        print(f"  {k:24s} = {c[k]}")
    print(f"  POSITIVE_PATH")
    print(f"    invariant_preservation = {c['POSITIVE_PATH']['invariant_preservation']}")
    print(f"    escape_intervals       = {c['POSITIVE_PATH']['escape_intervals']}")
    print(f"  NEGATIVE_PATH")
    print(f"    injected_escape        = {c['NEGATIVE_PATH']['injected_escape']}")
    print(f"    escape_detected        = {c['NEGATIVE_PATH']['escape_detected']}")
    print(f"    detected_intervals     = {c['NEGATIVE_PATH']['detected_intervals']}")
    for k in ("TRAJECTORY_HASH", "CONFIG_HASH", "H0_STATUS", "AUTHORITY", "CANON", "RECEIPT_HASH"):
        print(f"  {k:24s} = {c[k]}")
    print(f"  ⚠ {c['H0_EPISTEMIC_GUARD']}")
    print(f"  ✓ max admissible: {c['MAX_ADMISSIBLE_POSITIVE_STATEMENT']}")
    print(f"  ✓ negative control: {c['NEGATIVE_CONTROL_RESULT']}")
    print("─" * 66)
    print("  BEAUTY ≠ IDENTITY ≠ CONTROL · PIXEL CHANGE ≠ IDENTITY CHANGE · VERIFIER ≠ GROUND TRUTH")
    print("  DETECTED DRIFT ≠ KNOWN CAUSE · FULL REGEN ≠ LOCAL REPAIR · ONE CLIP ≠ RESULT")
    print(f"  VERDICT: CONTROL LAYER TESTABLE ({'PASS' if ok_L1 else 'FAIL'}) · "
          f"RENDER+VERIFY BLOCKED · VIDEO CLAIM = 🟣 CANDIDATE (experiment NOT run)")

    receipt = {"schema": "HELEN_VIDEO_V0_HARNESS", "canonical": canonical,
               "authority": False, "canon": False,
               "claim": "NO_CLAIM", "status": "CANDIDATE", "authority_delta": 0, "fable_calls": 0,
               "spec_S": S, "layers": {"L1_control": R, "L1_detail_lawful": a, "L1_detail_drift": b,
                                       "L2_render": L2, "L3_verify": L3},
               "J_vector": Jvec, "experiment": experiment, "ssr_loop": ssr,
               "verdict": "CONTROL_TESTABLE_RENDER_BLOCKED" if ok_L1 else "FAIL",
               "law": "consistent avatar = motion inside admissible class · x_t=π_face(𝓗_t) · "
                      "L1≠L2≠L3 (never identified) · R2>R1 is an EXPERIMENT not a claim · no pixel rendered",
               "caveat": "generator slot empty; a real run needs an open video prior + independent "
                         "verifier + (if a real identity) consent; no clip was produced or claimed"}
    (Path(__file__).resolve().parent / "HELEN_VIDEO_V0_HARNESS_RECEIPT.json").write_text(
        json.dumps(receipt, indent=2, ensure_ascii=False))
    print("  → HELEN_VIDEO_V0_HARNESS_RECEIPT.json")


if __name__ == "__main__":
    main()
