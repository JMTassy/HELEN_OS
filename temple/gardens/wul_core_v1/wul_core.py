#!/usr/bin/env python3
"""
WUL_CORE_V1 — typed inspection IR for governed HELEN state (spec-as-conformance-suite).

Architecture:   T  <—C—>  W  —Φ—>  P
  T typed state · W canonical WUL · P presentation (lossy).
Laws (executable, not prose):
  round-trip     P_W(C(T)) = T                    (canonical WUL parses back exactly)
  determinism    T1=T2 ⇒ C(T1)=C(T2)
  idempotence    N(N(w)) = N(w)
  normal round   C(P_W(w)) = N(w)
  FIREWALL       P ↛ T   (presentation cannot mint semantics — decorative WUL does NOT parse)
  typing         Δ ⊢ e:τ ; a governed step e1 —o,w→ e2 needs the witnesses for the state jump,
                 else STATIC TYPE ERROR (🌿→⚪ shortcut is rejected, not rendered)
  equivalence    Eq(p,q) ∈ {0,1,U}^5  (∼_R,∼_F,∼_E,∼_Γ,∼_replay) — ∼_F ⇏ ∼_E ⇏ ∼_Γ
  namespaces     ψ^wul ↛ ψ^phys  (anti-metaphor-leak; no implicit cross-namespace cast)

Δ = typing context · Γ = constitutional boundary (kept notationally distinct).
authority=false · canon=false · ΔA=0 · ΔΓ=0 · NO_MODEL_CALL · NO_COMMIT · NO_PUSH.
"""
import json, re
from pathlib import Path

# ---- Σ: canonical token glyphs (disjoint field alphabets) ----
ACTOR = {"🃏": "GOBLIN", "🛡": "HAL", "👑": "MAYOR", "🧠": "HER"}
OP    = {"🧪": "DISCRIMINATE", "🔥": "TEST", "🔀": "TRANSFORM", "🔬": "OBSERVE", "⚖": "GOVERN"}
STATE = {"🌿": "POSSIBILITY", "🟣": "CANDIDATE", "🔵": "OBSERVATION", "🟡": "WARRANT",
         "🟢": "ADMITTED", "⚪": "REPLAYABLE", "⚫": "DEAD"}
RANK  = {"POSSIBILITY": 0, "CANDIDATE": 1, "OBSERVATION": 2, "WARRANT": 3, "ADMITTED": 4, "REPLAYABLE": 5}
WITNESS_FOR = {1: "proposal", 2: "test_receipt", 3: "evidence", 4: "admission", 5: "receipt"}
INV = lambda d: {v: k for k, v in d.items()}
G_ACTOR, G_OP, G_STATE = INV(ACTOR), INV(OP), INV(STATE)

FIELD_ORDER = ["actor", "operation", "semantic_state", "object_id", "authority_delta"]

# ---------- C : T -> W  (deterministic canonical compile) ----------
def C(T):
    parts = [G_ACTOR[T["actor"]] + T["actor_id"],
             G_OP[T["operation"]],
             G_STATE[T["semantic_state"]],
             "#" + T["object_id"],
             "ΔA" + str(T["authority_delta"])]
    return "·".join(parts)

# ---------- P_W : W -> T  (partial parser; canonical WUL only) ----------
def P_W(w):
    if any(ch in w for ch in ["\x1b", "╔", "╗", "🌈", "║"]):     # ornamented/rendered → not canonical
        return None
    toks = w.split("·")
    if len(toks) != 5: return None
    a, o, s, obj, ad = [t.strip() for t in toks]
    try:
        actor_glyph = a[0]
        if actor_glyph not in ACTOR or o not in STATE and o not in OP: pass
        T = {"actor": ACTOR[actor_glyph], "actor_id": a[1:],
             "operation": OP[o], "semantic_state": STATE[s],
             "object_id": obj[1:] if obj.startswith("#") else None,
             "authority_delta": int(ad[2:]) if ad.startswith("ΔA") else None}
    except (KeyError, ValueError, IndexError):
        return None
    if T["object_id"] is None or T["authority_delta"] is None: return None
    return T

# ---------- N : normalization (idempotent) ----------
def N(w):
    t = P_W(w)
    return C(t) if t is not None else w   # canonical form is already normal; non-canonical unchanged

# ---------- Φ : W -> P  (lossy presentation; deliberately non-invertible) ----------
def PHI(w):
    return f"╔═ 🌈 ═╗ \x1b[36m{w}\x1b[0m 💎"      # ANSI + ornament → P_W() must reject

# ---------- Δ ⊢ governed transition ----------
def type_transition(s_from, s_to, witnesses):
    """Δ;Γ ⊢ e1 --o,w--> e2 : need every intermediate witness for the state-rank jump."""
    rf, rt = RANK[s_from], RANK[s_to]
    if rt <= rf:
        return {"ok": False, "error": "NON_ADVANCING_TRANSITION"}
    need = [WITNESS_FOR[r] for r in range(rf + 1, rt + 1)]
    missing = [wn for wn in need if wn not in witnesses]
    return {"ok": len(missing) == 0, "required": need, "missing": missing,
            "error": None if not missing else "STATIC_TYPE_ERROR:missing_witness"}

# ---------- typed equivalence signature ----------
def eq_sig(p, q):
    def v(a, b): return 1 if a == b else 0
    def key(x, cs): return tuple(x.get(c) for c in cs)
    E_R = v(key(p, ["x","y","fout","dec","ev","auth","gamma"]), key(q, ["x","y","fout","dec","ev","auth","gamma"]))
    E_F = v(key(p, ["x","y","fout","dec"]), key(q, ["x","y","fout","dec"]))
    E_E = v(key(p, ["x","y","fout","dec","ev"]), key(q, ["x","y","fout","dec","ev"]))
    E_G = v(key(p, ["x","y","gamma","auth"]), key(q, ["x","y","gamma","auth"]))
    E_RP = "U" if (p.get("replay") is None or q.get("replay") is None) else v(p["replay"], q["replay"])
    return (E_R, E_F, E_E, E_G, E_RP)

# ---------- namespace anti-leak ----------
def namespace_cast(sym, from_ns, to_ns, justified=False):
    if from_ns != to_ns and not justified:
        return {"ok": False, "error": f"NAMESPACE_ERROR:{sym}^{from_ns} ↛ {sym}^{to_ns}"}
    return {"ok": True}


def main():
    results = []
    def check(name, ok, detail=""):
        results.append({"test": name, "pass": bool(ok), "detail": detail})

    # 1. round-trip on canonical WUL
    T1 = {"actor": "GOBLIN", "actor_id": "07", "operation": "DISCRIMINATE",
          "semantic_state": "POSSIBILITY", "object_id": "O19", "authority_delta": 0}
    w1 = C(T1)
    check("round_trip  P_W(C(T))=T", P_W(w1) == T1, w1)

    # 2. determinism
    check("compiler_deterministic", C(T1) == C(dict(T1)))

    # 3. normalization idempotent
    check("N idempotent  N(N(w))=N(w)", N(N(w1)) == N(w1))
    check("normal round  C(P_W(w))=N(w)", C(P_W(w1)) == N(w1))

    # 4. FIREWALL: presentation cannot mint semantics  (P ↛ T)
    rendered = PHI(w1)
    check("P ↛ T  (rendered WUL does NOT parse back)", P_W(rendered) is None, rendered[:30] + "…")

    # 5. ill-typed shortcut  🌿 → ⚪  with no witnesses
    bad = type_transition("POSSIBILITY", "REPLAYABLE", witnesses=set())
    check("illtyped 🌿→⚪ rejected (STATIC_TYPE_ERROR)", (not bad["ok"]) and bad["missing"],
          "missing=" + ",".join(bad["missing"]))

    # 6. well-typed full protocol chain with all witnesses
    good = type_transition("POSSIBILITY", "REPLAYABLE",
                           witnesses={"proposal", "test_receipt", "evidence", "admission", "receipt"})
    check("welltyped protocol accepted", good["ok"], "required=" + ",".join(good["required"]))

    # 7. equivalence signature: ∼_F=1 but ∼_E=0 (and ∼_E=1 but ∼_Γ=0)
    pF = {"x":"raw","y":"ver","fout":"V","dec":"ADMIT","ev":"r1","auth":"W_mayor","gamma":True,"replay":"c1"}
    qF = {"x":"raw","y":"ver","fout":"V","dec":"ADMIT","ev":"r2","auth":"W_mayor","gamma":True,"replay":"c1"}
    sigF = eq_sig(pF, qF)
    check("Eq ∼_F ⇏ ∼_E  (1,1,0,·,·)", sigF[1] == 1 and sigF[2] == 0, f"Eq={sigF}")
    pG = {"x":"raw","y":"ver","fout":"V","dec":"ADMIT","ev":"r1","auth":"W_mayor","gamma":True,"replay":"c1"}
    qG = {"x":"raw","y":"ver","fout":"V","dec":"ADMIT","ev":"r1","auth":"W_none","gamma":False,"replay":"c1"}
    sigG = eq_sig(pG, qG)
    check("Eq ∼_E ⇏ ∼_Γ  (·,1,1,0,·)", sigG[2] == 1 and sigG[3] == 0, f"Eq={sigG}")

    # 8. namespace anti-leak
    leak = namespace_cast("ψ", "wul", "phys")
    check("namespace ψ^wul ↛ ψ^phys rejected", not leak["ok"], leak["error"])
    okcast = namespace_cast("ψ", "wul", "wul")
    check("same-namespace cast allowed", okcast["ok"])

    SOUND = all(r["pass"] for r in results)

    out = {"spec": "WUL_CORE_V1", "authority": False, "canon": False, "authority_delta": 0,
           "gamma_delta": 0, "model_calls": 0,
           "components": {"Σ_actor": ACTOR, "Σ_op": OP, "Σ_state": STATE, "state_rank": RANK},
           "laws_conformance": results, "SOUND": SOUND,
           "notation_fix": "Δ ⊢ e:τ (typing context) · Γ = constitutional boundary (distinct symbols)",
           "MAX_ADMISSIBLE_STATEMENT":
               "WUL_CORE_V1 canonical WUL round-trips (P_W∘C=id) and normalizes idempotently; presentation "
               "is lossy and NON-invertible (P↛T); ill-typed governed shortcuts are static type errors; "
               "equivalence is a {0,1,U}^5 signature preserving ∼_F⇏∼_E⇏∼_Γ; cross-namespace casts are rejected.",
           "GAPS_still_open": ["type lattice 𝒯 partial", "witness schema informal",
                               "Eq U-algebra = status label (not yet Kleene)", "grammar/escaping not frozen",
                               "path types (capability topology) not yet in 𝒯"],
           "commit_status": "NO_COMMIT", "push_status": "NO_PUSH", "next_verb": "HUMAN_REVIEW"}
    (Path(__file__).resolve().parent / "WUL_CORE_V1_RECEIPT.json").write_text(json.dumps(out, indent=2, ensure_ascii=False))

    print("═" * 78)
    print("  WUL_CORE_V1 — typed inspection IR  ·  T <—C—> W —Φ—> P  ·  conformance suite")
    print("═" * 78)
    print(f"  canonical example:  T → W =  {w1}")
    print(f"  rendered (lossy) Φ(W) =  {PHI(w1)}")
    print("─" * 78)
    for r in results:
        print(f"    {'✅' if r['pass'] else '❌'} {r['test']:42s} {r['detail']}")
    print("─" * 78)
    print(f"  WUL_CORE_V1 CONFORMANT = {SOUND}   ·   Δ⊢e:τ (typing) ⟂ Γ (governance)")
    print(f"  ΔA=0 · ΔΓ=0 · model_calls=0 · NO_COMMIT · → WUL_CORE_V1_RECEIPT.json")


if __name__ == "__main__":
    main()
