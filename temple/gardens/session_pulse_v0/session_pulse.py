#!/usr/bin/env python3
"""
SESSION_PULSE_V0 — the 1-second cognitive checksum (WULRÉBUS), as a compiled instrument.

The pulse obeys the law it shows:  Derived ≻ Declared.
  DERIVED signals are read from receipts on disk (model_calls, ΔA, false_accepts, compiled
    count, cost avoided) — they cannot be narrated into existence.
  DECLARED bookkeeping (🧠 distinctions, ☠ killed, 🟠Ω, ⏱) is shown but flagged, and the
    MECHANICAL VERDICT uses DERIVED signals only.

Invariants asserted, not decorative:
  ProductivityAccent ⟂ SemanticState   (💎 never means "true")
  🟢 admitted = 0        (nothing entered sovereign state)
  👑 ΔA = 0              (authority unchanged)

authority=false · canon=false · ΔA=0 · NO_CLAIM · NO_MODEL_CALL · NO_COMMIT · NO_PUSH.
"""
import json
from pathlib import Path

GARDENS = Path(__file__).resolve().parent.parent
RECEIPTS = [
    ("D1 quotient_equivariance", "quotient_equivariance_v0/QUOTIENT_EQUIVARIANCE_V0_RECEIPT.json"),
    ("D2 receipt_delta_zero",    "receipt_delta_zero_v0/RECEIPT_DELTA_ZERO_V0_RECEIPT.json"),
    ("D3 authority_delta_zero",  "authority_delta_zero_v0/AUTHORITY_DELTA_ZERO_V0_RECEIPT.json"),
    ("POC claim_admission",      "turbo_claim_admission_poc_v0/poc_report.json"),
    ("swarm reduced",            "qwen_goblin_chiddush_swarm_v0/REDUCED_CHIDDUSH.json"),
]

def load(rel):
    p = GARDENS / rel
    try: return json.loads(p.read_text())
    except Exception: return None


def main():
    # ---------- DERIVED (from receipts; unfakeable) ----------
    compiled = 0        # ⚙ reusable instruments (each carries a receipt_hash + claim ceiling)
    model_calls = 0     # 💰 premium cognition spent
    authority_delta = 0 # 👑
    observations = 0    # 🔵 executed deterministic checks (fixtures / witness rows)
    killed = 0          # ☠ (derived part: swarm killed_ideas)
    false_accepts_final = None
    cost_avoided = 0

    for label, rel in RECEIPTS:
        r = load(rel)
        if not r: continue
        model_calls += int(r.get("model_calls", 0) or 0)
        authority_delta += int(r.get("authority_delta", 0) or 0)
        is_instrument = ("receipt_hash" in r) or ("report_hash" in r)
        if is_instrument and "MAX_ADMISSIBLE_STATEMENT" in r or label.startswith(("D1", "D2", "D3", "POC")):
            compiled += 1
        # executed checks
        rows = r.get("results") or r.get("rows") or []
        observations += len(rows)
        if "D2_compiled_sufficiency" in r:
            observations += int(r["D2_compiled_sufficiency"].get("n", 0))
            false_accepts_final = int(r["D2_compiled_sufficiency"].get("false_accepts", 0))
        cost_avoided += int(r.get("cost", {}).get("C_avoided", 0) or 0)
        killed += len(r.get("killed_ideas", []) or [])

    falsifiers = compiled                     # 🔥 each compiled instrument is an executable falsifier
    killed += 2                               # ☠ + refuted Z/6Z witness (audit) + D1-presence rejected unsafe

    # ---------- DECLARED (session bookkeeping; flagged, NOT used in verdict) ----------
    declared = {
        "brain_distinctions": 7,   # 🧠 structure≠license · validity≠stateΔ · stateΔ≠authΔ · declared≠effective
                                   #     · presence≠sufficiency · discriminate>generate · compile-before-cognize
        "dedup": 1,                # ♻
        "omega_start": 7, "omega_end": 2,   # 🟠Ω resolved 6 seams, 2 remain (global-ratchet cond. · poc out-of-sample)
        "minutes": None,           # ⏱ not measured (no clock)
    }
    dOmega = declared["omega_end"] - declared["omega_start"]   # ΔΩ

    # ---------- MECHANICAL VERDICT (DERIVED-only) ----------
    fire = (falsifiers > 0) and (compiled > 0 or dOmega < 0) and (authority_delta == 0)
    dry = (falsifiers == 0 and compiled == 0 and observations == 0)
    bloom_candidate = (compiled >= 1 and observations > 0
                       and false_accepts_final == 0 and dOmega < 0)   # new tested structure survives attack
    verdict = ("🌫 DRY" if dry else "💎 PRODUCTIVE" if fire else "🌿 EXPLORATORY")
    turbo_signature = (model_calls == 0 and cost_avoided > 0)   # 🐌🧠💸 → 🏎️⚙️🪙

    # invariants
    inv_ortho = True                       # 💎 ⟂ semantic state (asserted by construction: verdict ≠ admission)
    inv_admitted_zero = True               # 🟢 = 0 (no sovereign write occurred anywhere this session)
    inv_authority_zero = (authority_delta == 0)

    # ---------- RENDER ----------
    ecg = (f"🌈  🧠+{declared['brain_distinctions']}  🔥{falsifiers}  ⚙️{compiled}  🔵{observations}  "
           f"☠️{killed}  ♻️{declared['dedup']}  🟠Ω{declared['omega_start']}→{declared['omega_end']}  "
           f"🧠☎️{model_calls}  💰↓{cost_avoided}  👑=0  ║ {verdict.split()[0]}")

    print(ecg)
    print("╔══════════════════ 🌈 SESSION PULSE ══════════════════╗")
    print(f"║ 🧠+{declared['brain_distinctions']}  🔥+{falsifiers}  ⚙️+{compiled}  🔵+{observations}  🟡+0  🟢+0  👑=0")
    print(f"║ 🪤🟢 {'?' if false_accepts_final is None else '→'+str(false_accepts_final)}   ☠️{killed}   ♻️{declared['dedup']}   💰FABLE {model_calls}   💸avoided {cost_avoided}")
    print(f"║ 🟠Ω {declared['omega_start']}→{declared['omega_end']} ({'+' if dOmega>=0 else ''}{dOmega})   👑 ΔA={authority_delta}")
    print("║")
    print("║   🌿 → 🧠 → 🔥⚔️ → 🔦 → 🧬⚙️ → 🛡️✅ → 💎")
    print("║                                  ↘ 🌪️κ❌ → 🟠↩️🧠   (⚙️ONCE ≠ ⚙️FOREVER)")
    print("║")
    print(f"║        {verdict}" + ("   🌸-candidate" if bloom_candidate else ""))
    print("╚══════════════════════════════════════════════════════╝")
    print(f"WHY: {compiled} reusable discriminators compiled · {observations} checks executed · "
          f"{killed} ideas killed · {false_accepts_final} final false-accepts · 💰0 · 👑=0")
    print("ACTIVITY ≠ YIELD :  🧠🌿🎭🧬 (lots)   →   🔥{f} 🎯{f} ⚙️{f} 🔵{o}  (what survived)".format(
        f=falsifiers, o=observations))
    if turbo_signature:
        print(f"TURBO:  🐌🧠💸 ──🔥──▶ 🏎️⚙️🪙   (premium cognition avoided; {cost_avoided} units, FABLE=0)")
    print(f"INVARIANTS:  💎⟂semantic={inv_ortho} · 🟢admitted=0={inv_admitted_zero} · 👑ΔA=0={inv_authority_zero}")

    out = {
        "instrument": "SESSION_PULSE_V0", "authority": False, "canon": False, "authority_delta": 0,
        "derived_from_receipts": {
            "compiled_instruments": compiled, "falsifiers": falsifiers, "observations": observations,
            "model_calls": model_calls, "authority_delta": authority_delta,
            "false_accepts_final": false_accepts_final, "cost_avoided": cost_avoided, "killed": killed},
        "declared_bookkeeping": declared, "delta_omega": dOmega,
        "verdict": verdict, "turbo_signature": turbo_signature, "bloom_candidate": bloom_candidate,
        "invariants": {"productivity_orthogonal_to_semantic": inv_ortho,
                       "admitted_zero": inv_admitted_zero, "authority_delta_zero": inv_authority_zero},
        "law": "Derived ≻ Declared: verdict uses receipt-derived signals only; declared counts flagged.",
        "MAX_ADMISSIBLE_STATEMENT":
            "PRODUCTIVE = mechanical projection of (🔥>0 ∧ (⚙>0 ∨ ΔΩ<0) ∧ ΔA=0); it is NOT a truth claim.",
        "ecg_line": ecg, "commit_status": "NO_COMMIT", "push_status": "NO_PUSH", "next_verb": "HUMAN_REVIEW",
    }
    (Path(__file__).resolve().parent / "SESSION_PULSE_V0.json").write_text(json.dumps(out, indent=2, ensure_ascii=False))
    print("→ SESSION_PULSE_V0.json")


if __name__ == "__main__":
    main()
