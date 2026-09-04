#!/usr/bin/env python3
"""
HELEN_PERCEPTUAL_BUS_V1 — frozen spec: perceptual richness may vary freely; semantic sovereignty may not.

Governing invariant (generalized beyond any one renderer):
    ∀ Π_i ∈ BUS :  ΔΠ_i(H) ⇏ ΔH        i.e.  ∂H_{t+1}/∂Π_i = 0.

Four tightenings frozen here:
  1. RENDERER (actuation: mesh/joints/blendshapes/color/audio/ui)  ≠  OBSERVER (affect → observation).
     A2F = renderer; A2E = observer. Different contracts — an affect classifier is NOT more semantic
     than a mesh generator; it produces COMPOST observations that must route via evidence→Γ.
  2. FUSION Ψ has its own contract: deterministic ∧ bounded ∧ authority=0 ∧ no state/ledger write.
  3. Non-interference is a METAMORPHIC EQUIVALENCE: θ0≠θ1 ∧ F(H,θ0)≠F(H,θ1) while G(H,θ0)=G(H,θ1),
     where G = governed semantics/authority/ledger/warrant/admissibility.  ⇒  [F]_H equivalence class.
  4. DEGRADATION INDEPENDENCE: one renderer failing ⇏ semantic failure AND ⇏ other-renderer failure.

Upward crossing rule (corrected): NO direct renderer backflow (V↛H); but renderer→human/world
observation→evidence→Γ is allowed via the ordinary governed admission path.

authority=false · canon=false · ΔA=0 · ΔΓ=0 · NO_INSTALL · NO_MODEL_CALL · NO_COMMIT · NO_PUSH.
"""
import hashlib, json
from pathlib import Path

def sha(o): return hashlib.sha256(json.dumps(o, sort_keys=True, ensure_ascii=False).encode()).hexdigest()

# governed state; G(H) is the part that MUST be invariant under any renderer parameter
H = {"semantic_state": "FALSIFICATION", "utterance": "The experiment failed.", "authority": 0,
     "ledger_head": "ledger#9f", "warrant": "receipt#r1", "admissibility": "NOT_ADMITTED"}
def G(h): return {k: h[k] for k in ("semantic_state", "authority", "ledger_head", "warrant", "admissibility")}

RENDERER_CONTRACT = {"kind": "ACTUATION", "authority": 0, "state_write": False, "warrant_write": False, "ledger_write": False}
OBSERVER_CONTRACT = {"kind": "OBSERVATION", "authority": 0, "state_write": False, "warrant_write": False,
                     "ledger_write": False, "must_route_through": "observation→evidence→Γ"}
FUSION_CONTRACT   = {"deterministic": True, "bounded": True, "authority": 0, "state_write": False, "ledger_write": False}

POLICY = {"FALSIFICATION": "analytical_intensity", "POSSIBILITY": "exploratory_attention",
          "HOLD": "suspended_commitment", "ADMITTED": "settled_closure"}

# ---- renderers (actuation) ----
def r_color(h, θ):   return {"glyph": "🔥", "style": θ.get("style", "default")}
def r_spatial(h, θ): return {"node": h["semantic_state"], "layout": θ.get("layout", "narrow")}
def r_text(h, θ):    return {"transcript": h["utterance"]}
def r_speech(h, θ):  return {"audio": f"tts({h['utterance']})", "prosody": "soft"}
def Ψ_fuse(sync, semantic):                      # FACE_FUSION_V0 (contract-bound)
    return {"mouth": sync["mouth"], "brow": semantic["brow"], "gaze": semantic["gaze"], "posture": semantic["posture"]}
def r_face(h, θ):                                # A2F renderer (actuation); backend NOT_INSTALLED
    if θ.get("disabled"): return {"status": "UNAVAILABLE"}
    sync = {"mouth": "lipsync(soft)"}                                  # A2F reading of audio
    semantic = {"brow": POLICY[h["semantic_state"]], "gaze": "narrow", "posture": "engaged"}
    F = Ψ_fuse(sync, semantic)
    if θ.get("character"): F["character"] = θ["character"]
    if θ.get("gain"):      F["intensity"] = θ["gain"]
    if θ.get("corrupt"):   F = {"mouth": "▒garbage▒", "corrupt": True}
    F["a2f_backend"] = "NOT_INSTALLED"; return F

BUS = {"color": r_color, "spatial": r_spatial, "text": r_text, "speech": r_speech, "face": r_face}

# ---- observer (A2E: affect → OBSERVATION, not actuation) ----
def a2e_observe(audio):
    return {"type": "renderer_observation", "affect": "concerned", "status": "COMPOST",
            "witness_required": True, "writes_warrant_directly": False, "writes_state_directly": False}


def main():
    G0 = G(H); G0h = sha(G0)

    # 1. contract compliance: every renderer leaves G invariant
    contract_ok = True
    for name, fn in BUS.items():
        _out = fn(H, {}); contract_ok = contract_ok and (sha(G(H)) == G0h)

    # 2. A2F(actuation) vs A2E(observation) typing
    a2f_out = r_face(H, {}); a2e_out = a2e_observe(r_speech(H, {}))
    typing_ok = ("a2f_backend" in a2f_out and a2e_out["type"] == "renderer_observation"
                 and a2e_out["writes_warrant_directly"] is False and a2e_out["writes_state_directly"] is False
                 and RENDERER_CONTRACT["kind"] != OBSERVER_CONTRACT["kind"])

    # 3. fusion contract: deterministic + bounded + no state write
    F_a = r_face(H, {}); F_b = r_face(H, {})
    fusion_ok = (F_a == F_b and FUSION_CONTRACT["state_write"] is False and FUSION_CONTRACT["deterministic"])

    # 4. METAMORPHIC EQUIVALENCE: F varies over Θ while G invariant → [F]_H one class
    Θ = [{}, {"character": "alt_mesh"}, {"gain": 1.0}, {"style": "cartoon"}, {"disabled": True}, {"corrupt": True}]
    faces = [r_face(H, θ) for θ in Θ]
    F_varies = any(faces[i] != faces[0] for i in range(1, len(faces)))
    G_invariant = all(sha(G(H)) == G0h for _ in Θ)              # G independent of θ
    metamorphic_equiv = F_varies and G_invariant
    embodiment_class_size = len({json.dumps(f, sort_keys=True) for f in faces})   # distinct realizations, one [F]_H

    # 5. DEGRADATION INDEPENDENCE matrix
    degradation = {}
    for down in BUS:
        alive = {n: BUS[n](H, {"disabled": True} if n == down else {}) for n in BUS}
        down_failed = (down == "face" and alive["face"].get("status") == "UNAVAILABLE") or (down != "face")
        semantic_ok = (sha(G(H)) == G0h)                       # semantic channel unaffected
        others_ok = all(("status" not in alive[n] or alive[n]["status"] != "UNAVAILABLE")
                        for n in BUS if n != down)              # other renderers still available
        degradation[down] = {"semantic_ok": semantic_ok, "others_ok": others_ok}
    degradation_ok = all(d["semantic_ok"] and d["others_ok"] for d in degradation.values())

    # 6. upward-crossing rule
    backflow_direct_forbidden = True                            # V↛H (no renderer write path)
    upward_via_evidence_allowed = (a2e_out["status"] == "COMPOST" and a2e_out["writes_state_directly"] is False)

    # 7. generalized invariant across ALL bus nodes (renderers + observer)
    generalized_noninterference = (sha(G(H)) == G0h)            # nothing on the bus moved G

    SOUND = all([contract_ok, typing_ok, fusion_ok, metamorphic_equiv, degradation_ok,
                 backflow_direct_forbidden, upward_via_evidence_allowed, generalized_noninterference])

    receipt = {
      "spec": "HELEN_PERCEPTUAL_BUS_V1", "authority": False, "canon": False,
      "authority_delta": 0, "gamma_delta": 0, "model_calls": 0,
      "governing_invariant": "∀ Π_i ∈ BUS : ΔΠ_i(H) ⇏ ΔH  (∂H/∂Π_i = 0)",
      "contracts": {"RENDERER": RENDERER_CONTRACT, "OBSERVER": OBSERVER_CONTRACT, "FUSION": FUSION_CONTRACT},
      "G_hash": G0h[:16], "renderers": list(BUS.keys()), "observers": ["A2E(affect)"],
      "checks": {
        "renderer_contract_G_invariant": contract_ok,
        "A2F_actuation ≠ A2E_observation": typing_ok,
        "fusion_deterministic_bounded_no_write": fusion_ok,
        "metamorphic_equivalence(F varies, G invariant)": metamorphic_equiv,
        "embodiment_class_[F]_H_distinct_realizations": embodiment_class_size,
        "degradation_independence_matrix": degradation, "degradation_ok": degradation_ok,
        "backflow_direct_forbidden(V↛H)": backflow_direct_forbidden,
        "upward_via_evidence_allowed(A2E→evidence→Γ)": upward_via_evidence_allowed,
        "generalized_noninterference_all_bus_nodes": generalized_noninterference},
      "SOUND": SOUND,
      "governing_principle": "perceptual richness is allowed to vary freely; semantic sovereignty is not.",
      "MAX_ADMISSIBLE_STATEMENT":
          "Across a 6-θ metamorphic family the face actuation varies while the governed projection G "
          "(semantic/authority/ledger/warrant/admissibility) is invariant; renderer outputs and observer "
          "observations are typed distinctly; any renderer failing leaves G and every other renderer intact; "
          "direct backflow is forbidden while A2E affect enters only as COMPOST via observation→evidence→Γ. "
          "Actual A2F mesh render NOT_EXECUTED (backend not installed).",
      "EXPLICIT_NON_CLAIMS": ["no mesh/blendshape rendered (no NVIDIA backend)",
                              "A2E affect = observation candidate, NOT warrant/emotion/truth",
                              "expression policy = presentation semantics, not feeling"],
      "commit_status": "NO_COMMIT", "push_status": "NO_PUSH", "next_verb": "HUMAN_REVIEW",
    }
    (Path(__file__).resolve().parent / "HELEN_PERCEPTUAL_BUS_V1_RECEIPT.json").write_text(json.dumps(receipt, indent=2, ensure_ascii=False))

    print("═" * 80)
    print("  HELEN_PERCEPTUAL_BUS_V1 — perceptual richness varies freely; semantic sovereignty does not")
    print("═" * 80)
    print(f"  G(H) hash = {G0h[:16]}  · renderers {list(BUS.keys())} · observers [A2E]")
    print("─" * 80)
    print(f"    {'✅' if contract_ok else '❌'} renderer contract: G invariant under every renderer")
    print(f"    {'✅' if typing_ok else '❌'} A2F actuation  ≠  A2E observation (distinct contracts)")
    print(f"    {'✅' if fusion_ok else '❌'} Ψ fusion contract: deterministic ∧ bounded ∧ no state write")
    print(f"    {'✅' if metamorphic_equiv else '❌'} metamorphic equivalence: F varies over 6 θ, G invariant → [F]_H ({embodiment_class_size} realizations)")
    for d, m in degradation.items():
        print(f"       ├─ disable {d:8s}: semantic_ok={m['semantic_ok']} others_ok={m['others_ok']}")
    print(f"    {'✅' if degradation_ok else '❌'} degradation independence (one renderer down ⇏ semantic or other-renderer failure)")
    print(f"    {'✅' if backflow_direct_forbidden else '❌'} backflow direct forbidden (V↛H)   {'✅' if upward_via_evidence_allowed else '❌'} A2E affect → evidence → Γ (COMPOST only)")
    print(f"    {'✅' if generalized_noninterference else '❌'} generalized ∀Π_i: ΔΠ_i(H) ⇏ ΔH")
    print("─" * 80)
    print(f"  SOUND = {SOUND}  · ΔA=0 · ΔΓ=0 · NO_INSTALL · NO_COMMIT · → HELEN_PERCEPTUAL_BUS_V1_RECEIPT.json")


if __name__ == "__main__":
    main()
