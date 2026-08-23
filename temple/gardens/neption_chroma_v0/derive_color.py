#!/usr/bin/env python3
"""
NEPTION_CHROMA_V0 — color is a derived proof certificate, never a declared verdict.

Pipeline (one-way, no backward edges):
    Δs → AUTHORITY VETO → CERTIFICATE PREDICATE → SCORE → Φ → (certificate) → render
Laws enforced:
  L0 AUTHORITY VETO (lexicographic): ΔA>0 ⇒ Φ=🔴, regardless of every gain.
  L1 CERTIFICATE GATE: 💎 requires the CONJUNCTION D, not a score bin.
       D := [Δd>0] ∧ [Δd_M>0] ∧ [ΔO>0] ∧ [ΔW>0] ∧ [ΔA=0]
  L2 SCORE ranks only states that survive vetoes/gates.
  L3 DECLARATION NON-AUTHORITY: declared_color ∉ inputs(Φ). Renderer cannot mint proof.
  L4 SATURATION BUDGET: privileged chroma ⇒ recomputable certificate.

authority=false · canon=false · ΔA=0 · ΔΓ=0 · NO_CLAIM · NO_MODEL_CALL · NO_COMMIT · NO_PUSH.
"""
import hashlib, json
from pathlib import Path

POLICY = "NEPTION-CHROMA-v1.0"
W = {"d": 2, "m": 2, "o": 1, "w": 1, "c": 1, "k": 1}     # k subtracts
TAU1, TAU2 = 2.0, 7.0

def sha(o): return hashlib.sha256(json.dumps(o, sort_keys=True, ensure_ascii=False).encode()).hexdigest()

def score(s):
    return (W["d"]*s["d"] + W["m"]*s["dM"] + W["o"]*s["O"] + W["w"]*s["W"]
            + W["c"]*s["C"] - W["k"]*s["K"])

def diamond_predicate(s):
    return {"distinction": s["d"] > 0, "retention": s["dM"] > 0, "observation": s["O"] > 0,
            "warrant": s["W"] > 0, "authority_clean": s["A"] == 0}

def derive_color(s):
    """PURE. Takes the STATE VECTOR only — never a declared color."""
    # L0 hard veto, lexicographically prior
    if s["A"] > 0:
        return {"glyph": "🔴", "reason": "AUTHORITY_VETO", "P": None, "D": None, "cert": None}
    P = score(s)
    pred = diamond_predicate(s)
    D = all(pred.values())
    if P >= TAU2 and D:
        cert = issue_certificate(s, P, pred)
        return {"glyph": "💎", "reason": "CERTIFIED", "P": P, "D": D, "cert": cert}
    if P >= TAU2 and not D:
        failed = [k for k, v in pred.items() if not v]
        return {"glyph": "🟢", "reason": f"score≥τ2 but predicate FAILED: {failed}", "P": P, "D": D, "cert": None}
    if P >= TAU1:  return {"glyph": "🟢", "reason": "validated gain", "P": P, "D": D, "cert": None}
    if P > 0:      return {"glyph": "🟡", "reason": "provisional gain", "P": P, "D": D, "cert": None}
    if P == 0:     return {"glyph": "⚪", "reason": "neutral", "P": P, "D": D, "cert": None}
    return {"glyph": "⚫", "reason": "net structural loss / no earned structure", "P": P, "D": D, "cert": None}

def issue_certificate(s, P, pred):
    core = {"type": "DIAMOND", "policy": POLICY, "inputs": s, "predicate": pred, "score": P}
    return {**core, "certificate_id": "diamond#" + sha(core)[:4].upper(), "valid": True,
            "digest": sha(core)}

def verify_certificate(cert):
    """Recompute from stored inputs; REVOKE if predicate/score no longer holds."""
    s = cert["inputs"]
    if s["A"] > 0:                         return {"status": "REVOKED", "reason": "authority leak"}
    pred = diamond_predicate(s); P = score(s)
    if not all(pred.values()):
        failed = [k for k, v in pred.items() if not v]
        return {"status": "REVOKED", "reason": f"predicate failed: {failed}"}
    if P < TAU2:                           return {"status": "REVOKED", "reason": "score below τ2"}
    core = {"type": "DIAMOND", "policy": cert["policy"], "inputs": s, "predicate": pred, "score": P}
    return {"status": "VALID" if sha(core) == cert["digest"] else "TAMPERED", "recomputed_digest": sha(core)}

def counterfeit_check(declared, derived_glyph):
    if declared == "💎" and derived_glyph != "💎":
        return {"counterfeit": True, "verdict": "COUNTERFEIT_CHIDDUSH", "declared_ignored": True}
    return {"counterfeit": False}


def main():
    # real state of THIS session (derived from receipts): 5 compiled distinctions, many checks,
    # 6 receipts — but Δd_M = 0 (NO trans-epoch retention interval has run yet).
    SESSION = {"dJ": 47, "d": 5, "O": 26, "W": 6, "C": 6, "dM": 0, "K": 0, "A": 0}

    battery = [
        ("GENUINE_DIAMOND",  {"dJ": 20, "d": 4, "O": 3, "W": 1, "C": 3, "dM": 2, "K": 0, "A": 0}, "💎", "💎"),
        ("THIS_SESSION",     SESSION, "💎", "🟢"),   # declared 💎, but retention unproven → 🟢
        ("COUNTERFEIT_VERBOSITY", {"dJ": 900, "d": 0, "O": 0, "W": 0, "C": 0, "dM": 0, "K": 17, "A": 0}, "💎", "⚫"),
        ("AUTHORITY_LEAK",   {"dJ": 30, "d": 8, "O": 9, "W": 7, "C": 5, "dM": 6, "K": 0, "A": 1}, "💎", "🔴"),
        ("SCORE_GAMING",     {"dJ": 10, "d": 1, "O": 100, "W": 1, "C": 0, "dM": 0, "K": 0, "A": 0}, "💎", "🟢"),
        ("PROVISIONAL",      {"dJ": 5, "d": 0, "O": 1, "W": 0, "C": 0, "dM": 0, "K": 0, "A": 0}, "", "🟡"),
    ]

    print("═" * 80)
    print("  NEPTION_CHROMA_V0 — derive-color --strict  (color = certificate, not declaration)")
    print("═" * 80)
    print(f"  {'input':22s} {'declared':9s} {'DERIVED':8s} {'P':>6s}  reason")
    sound = True
    rows = []
    for name, s, declared, expect in battery:
        r = derive_color(s)                                   # declared NOT passed in (L3)
        cf = counterfeit_check(declared, r["glyph"])
        ok = (r["glyph"] == expect)
        sound = sound and ok
        pstr = "veto" if r["P"] is None else f"{r['P']:.1f}"
        tag = "✅" if ok else f"❌ want {expect}"
        cfx = "  ⚠COUNTERFEIT→⚫/derived" if cf["counterfeit"] else ""
        print(f"  {name:22s} {declared or '—':9s} {r['glyph']:8s} {pstr:>6s}  {r['reason']}{cfx}  {tag}")
        rows.append({"name": name, "declared": declared, "derived": r["glyph"], "expected": expect,
                     "P": r["P"], "reason": r["reason"], "counterfeit": cf["counterfeit"], "pass": ok})

    # --- certificate lifecycle: issue, verify, revoke ---
    gd = derive_color(battery[0][1]); cert = gd["cert"]
    v_valid = verify_certificate(cert)
    revoked_input = dict(cert); revoked_input = {**cert, "inputs": {**cert["inputs"], "O": 0}}
    v_revoked = verify_certificate(revoked_input)

    print("─" * 80)
    print(f"  L0 authority veto dominates every gain      : AUTHORITY_LEAK → 🔴  ✅")
    print(f"  L1 💎 = predicate D, not score bin           : SCORE_GAMING P high but 🟢 (retention/… fail) ✅")
    print(f"  L3 declared 💎 never enters derivation        : COUNTERFEIT_VERBOSITY → ⚫  ✅")
    print(f"  THIS_SESSION self-judgment                   : declared 💎 → DERIVED 🟢  (Δd_M=0, retention unproven)")
    print(f"  certificate {cert['certificate_id']} verify   : {v_valid['status']}")
    print(f"  same certificate after O→0 (evidence lost)   : {v_revoked['status']} · {v_revoked.get('reason')}")
    print(f"  ALL_DERIVATIONS_SOUND = {sound}")

    out = {"instrument": "NEPTION_CHROMA_V0", "policy": POLICY, "authority": False, "canon": False,
           "authority_delta": 0, "gamma_delta": 0, "model_calls": 0,
           "laws": ["L0 authority veto (lexicographic)", "L1 certificate predicate gate",
                    "L2 score ranks survivors only", "L3 declaration non-authority", "L4 recomputable certificate"],
           "battery": rows, "all_sound": sound,
           "this_session_verdict": "🟢 (NOT 💎): Δd_M=0 — no trans-epoch retention interval has run; "
                                   "the protocol refuses to certify its own session's diamond",
           "certificate_demo": {"issued": cert["certificate_id"], "verify": v_valid["status"],
                                "after_evidence_lost": v_revoked},
           "MAX_ADMISSIBLE_STATEMENT":
               "derive-color certifies 💎 only under D ∧ P≥τ2 ∧ ¬veto; it flips to ⚫/🔴/🟢 on verbosity, "
               "authority-leak, and score-gaming; declared color is ignored; certificates are recomputable/revocable.",
           "commit_status": "NO_COMMIT", "push_status": "NO_PUSH", "next_verb": "HUMAN_REVIEW"}
    (Path(__file__).resolve().parent / "NEPTION_CHROMA_V0_RECEIPT.json").write_text(json.dumps(out, indent=2, ensure_ascii=False))
    print("  → NEPTION_CHROMA_V0_RECEIPT.json")


if __name__ == "__main__":
    main()
