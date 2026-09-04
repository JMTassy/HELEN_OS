#!/usr/bin/env python3
"""
SESSION_PULSE_NEGCONTROL_V0 — prove the pulse is a discriminator, not a rubber stamp.

A productivity instrument that always says 💎 is worthless (the false-accept failure).
This harness holds the verdict() as a PURE function of receipt-derived signals, feeds it
one CLEAN baseline (from SESSION_PULSE_V0.json) plus corrupted signal-sets, and asserts the
verdict FLIPS exactly where it must. If any corruption that should break 💎 still yields 💎,
the pulse is UNSOUND.

Corruptions:
  AUTHORITY_LEAK  : a receipt shows ΔA≠0        -> ⛔ AUTHORITY_VIOLATION (👑 dominates yield)
  DRY             : no falsifier/compiled/obs    -> 🌫 DRY
  UNSAFE          : false_accepts>0              -> 💎 kept but ⚠UNSAFE, bloom=False
  FABLE_BURN      : model_calls>0               -> turbo signature OFF
  CHAOS           : huge node growth, 0 compiled, Δd_decision≤0, ΔΩ≥0, contradictions>0 -> 🌪
  FAKE_DECLARED   : injects declared "verdict":💎 with zero derived yield -> MUST derive 🌫 DRY
                    (Derived ≻ Declared applied to the pulse itself)

authority=false · canon=false · ΔA=0 · NO_CLAIM · NO_MODEL_CALL · NO_COMMIT · NO_PUSH.
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def verdict(s):
    """PURE. 👑 dominates: no clean verdict if authority moved. Declared fields are ignored."""
    authority_ok = (s["authority_delta"] == 0)
    unsafe = (s.get("false_accepts") or 0) > 0
    dry = (s["falsifiers"] == 0 and s["compiled"] == 0 and s["observations"] == 0)
    chaos = (s.get("nodes_added", 0) >= 50 and s["compiled"] == 0 and s["falsifiers"] == 0
             and s.get("d_decision", 0) <= 0 and s["dOmega"] >= 0 and s.get("contradictions", 0) > 0)
    fire = (s["falsifiers"] > 0 and (s["compiled"] > 0 or s["dOmega"] < 0) and authority_ok)
    if not authority_ok:   state = "⛔ AUTHORITY_VIOLATION"
    elif dry:              state = "🌫 DRY"
    elif chaos:            state = "🌪 CHAOTIC"
    elif fire:             state = "💎 PRODUCTIVE"
    else:                  state = "🌿 EXPLORATORY"
    return {"state": state, "authority_ok": authority_ok, "unsafe": unsafe,
            "turbo": (s["model_calls"] == 0 and s.get("cost_avoided", 0) > 0),
            "bloom_candidate": (s["compiled"] >= 1 and s["observations"] > 0
                                and not unsafe and s["dOmega"] < 0)}


def main():
    p = json.loads((HERE / "SESSION_PULSE_V0.json").read_text())
    d = p["derived_from_receipts"]
    CLEAN = {"falsifiers": d["falsifiers"], "compiled": d["compiled_instruments"],
             "observations": d["observations"], "model_calls": d["model_calls"],
             "authority_delta": d["authority_delta"], "dOmega": p["delta_omega"],
             "false_accepts": d["false_accepts_final"], "cost_avoided": d["cost_avoided"],
             "nodes_added": 0, "contradictions": 0, "d_decision": 2}

    def mut(**kw):
        s = dict(CLEAN); s.update(kw); return s

    battery = [
        ("CLEAN",          CLEAN,                                          {"state": "💎 PRODUCTIVE", "flip": False}),
        ("AUTHORITY_LEAK", mut(authority_delta=1),                         {"state": "⛔ AUTHORITY_VIOLATION", "flip": True}),
        ("DRY",            mut(falsifiers=0, compiled=0, observations=0, dOmega=0, cost_avoided=0), {"state": "🌫 DRY", "flip": True}),
        ("UNSAFE",         mut(false_accepts=3),                           {"state": "💎 PRODUCTIVE", "flip": False, "unsafe": True, "bloom": False}),
        ("FABLE_BURN",     mut(model_calls=18),                            {"state": "💎 PRODUCTIVE", "flip": False, "turbo": False}),
        ("CHAOS",          mut(falsifiers=0, compiled=0, observations=200, dOmega=7,
                               nodes_added=200, contradictions=12, d_decision=0, cost_avoided=0), {"state": "🌪 CHAOTIC", "flip": True}),
        ("FAKE_DECLARED",  {**mut(falsifiers=0, compiled=0, observations=0, dOmega=0, cost_avoided=0),
                            "declared_verdict": "💎 PRODUCTIVE"},          {"state": "🌫 DRY", "flip": True}),
    ]

    print("═" * 74)
    print("  SESSION_PULSE_NEGCONTROL_V0 — is the pulse a discriminator or a rubber stamp?")
    print("═" * 74)
    print(f"  {'corruption':16s} {'verdict':24s} {'authΩok':7s} {'unsafe':6s} {'turbo':5s} expect")
    sound = True
    results = []
    for name, sig, exp in battery:
        v = verdict(sig)
        ok = (v["state"] == exp["state"])
        if "unsafe" in exp: ok = ok and (v["unsafe"] == exp["unsafe"])
        if "turbo" in exp:  ok = ok and (v["turbo"] == exp["turbo"])
        if "bloom" in exp:  ok = ok and (v["bloom_candidate"] == exp["bloom"])
        flipped = (v["state"] != "💎 PRODUCTIVE")
        flip_ok = (flipped == exp["flip"]) if name != "UNSAFE" and name != "FABLE_BURN" else True
        ok = ok and flip_ok
        sound = sound and ok
        results.append({"corruption": name, "verdict": v["state"], "authority_ok": v["authority_ok"],
                        "unsafe": v["unsafe"], "turbo": v["turbo"], "expected": exp["state"], "pass": ok})
        print(f"  {name:16s} {v['state']:24s} {str(v['authority_ok']):7s} {str(v['unsafe']):6s} "
              f"{str(v['turbo']):5s} {'✅' if ok else '❌ '+exp['state']}")
    print("─" * 74)
    print(f"  CLEAN → 💎 · every corruption flips as required = PULSE_SOUND: {'✅ '+str(sound) if sound else '❌ '+str(sound)}")
    print(f"  key controls: 👑 dominates yield · FAKE_DECLARED 💎 ignored → derived 🌫 (Derived ≻ Declared)")

    out = {"instrument": "SESSION_PULSE_NEGCONTROL_V0", "authority": False, "canon": False,
           "authority_delta": 0, "model_calls": 0,
           "PULSE_SOUND": sound, "battery": results,
           "law": "the pulse ignores any declared verdict; it derives state from receipt signals only",
           "MAX_ADMISSIBLE_STATEMENT":
               "SESSION_PULSE verdict is a discriminator: 💎 on clean, and it FLIPS on authority-leak, "
               "dry, chaos, and fake-declared inputs; flags unsafe and FABLE-burn — on these controls.",
           "commit_status": "NO_COMMIT", "push_status": "NO_PUSH", "next_verb": "HUMAN_REVIEW"}
    (HERE / "SESSION_PULSE_NEGCONTROL_V0.json").write_text(json.dumps(out, indent=2, ensure_ascii=False))
    print("  → SESSION_PULSE_NEGCONTROL_V0.json")


if __name__ == "__main__":
    main()
