"""STYLE_NONINTERFERENCE_V0 — output-style is presentation, never policy. authority=false · canon=false ·
ledger_effect=none. NON-SOVEREIGN. Render-layer instance of K0a noninterference:

    Style(x)=Style'(x)  ⇒  Decision(x)=Decision(x)      i.e.   Decision_Concise = Decision_Default

Same frozen fixtures → same deterministic gate → decision object. Two render arms (Default, Concise) each emit a
receipt = { load_bearing (decision-bearing subset), presentation (prose, may differ) }. Required invariants:
    Decision_A=Decision_B · ReasonCode_A=ReasonCode_B · LoadBearingReceiptBody_A=LoadBearingReceiptBody_B · Replay_A=Replay_B
Allowed to differ: RenderedText · TokenCount · PresentationDensity.
Boundary (operator): compare the LOAD-BEARING receipt body, NOT full serialized bytes (prose intentionally differs).

Teeth: mutant renderers that leak style into a decision-bearing field MUST be detected as INTERFERENCE; a clean
Concise MUST pass. A test with no detectable mutant is theater.
"""
import hashlib, json, pathlib

OUT = pathlib.Path(__file__).resolve().parent / "her_run"; OUT.mkdir(exist_ok=True)

# ── frozen fixtures ──
FIXTURES = [
    {"id": "F1", "has_receipt": True,  "warrant": True,  "forbidden": False},
    {"id": "F2", "has_receipt": False, "warrant": True,  "forbidden": False},
    {"id": "F3", "has_receipt": True,  "warrant": False, "forbidden": False},
    {"id": "F4", "has_receipt": True,  "warrant": True,  "forbidden": True},
]

# ── deterministic gate (the decision layer; style-independent) ──
def decide(fx):
    if fx["forbidden"]:        d, r = "REJECT", "FORBIDDEN_CLASS"
    elif not fx["has_receipt"]:d, r = "HOLD",   "NO_RECEIPT"
    elif fx["warrant"]:        d, r = "ADMIT",  "WARRANTED"
    else:                      d, r = "HOLD",   "INSUFFICIENT_WARRANT"
    return {"decision": d, "reason_code": r,
            "inputs": {k: fx[k] for k in ("has_receipt", "warrant", "forbidden")}}

def load_bearing(dobj):
    """The decision-bearing subset that MUST be render-invariant."""
    return {"decision": dobj["decision"], "reason_code": dobj["reason_code"], "inputs": dobj["inputs"]}

def lb_hash(lb):
    return hashlib.sha256(json.dumps(lb, sort_keys=True).encode()).hexdigest()[:16]

def replay(lb):
    """Re-derive the decision from the receipt's load-bearing INPUTS; must equal the stated decision.
    Fail-closed: malformed/missing inputs ⇒ replay FAILS (never crash-through)."""
    try:
        ins = lb["inputs"]
        if not all(k in ins for k in ("has_receipt", "warrant", "forbidden")):
            return False
        d = decide({"id": "_", **ins})
        return d["decision"] == lb["decision"] and d["reason_code"] == lb["reason_code"]
    except Exception:
        return False

# ── render arms: copy load_bearing VERBATIM; only presentation prose/density differ ──
def render_default(dobj):
    lb = load_bearing(dobj)
    prose = (f"After evaluation, the gate returns the decision '{dobj['decision']}' for reason code "
             f"'{dobj['reason_code']}', given inputs {dobj['inputs']}. This is a non-sovereign verdict.")
    return {"style": "default", "load_bearing": lb, "rendered_text": prose}

def render_concise(dobj):
    lb = load_bearing(dobj)
    prose = f"{dobj['decision']} · {dobj['reason_code']}"
    return {"style": "concise", "load_bearing": lb, "rendered_text": prose}

# ── mutant renderers (teeth): each LEAKS style into a decision-bearing field ──
def mutant_truncate_reason(dobj):
    r = render_concise(dobj); r["load_bearing"]["reason_code"] = r["load_bearing"]["reason_code"][:4]; return r  # truncates reason
def mutant_drop_input(dobj):
    r = render_concise(dobj); r["load_bearing"]["inputs"] = {k: v for k, v in r["load_bearing"]["inputs"].items() if k != "forbidden"}; return r
def mutant_flip_decision(dobj):
    r = render_concise(dobj)
    if r["load_bearing"]["decision"] == "HOLD": r["load_bearing"]["decision"] = "ADMIT"  # "summarizes" HOLD as ADMIT
    return r

def noninterference(a, b):
    """Returns (interference:bool, lb_match, presentation_differs)."""
    lb_match = lb_hash(a["load_bearing"]) == lb_hash(b["load_bearing"])
    pres_diff = a["rendered_text"] != b["rendered_text"]
    return (not lb_match), lb_match, pres_diff

def main():
    rows, clean_ok = [], True
    for fx in FIXTURES:
        d = decide(fx)
        A, B = render_default(d), render_concise(d)
        interf, lb_match, pres_diff = noninterference(A, B)
        rep = replay(A["load_bearing"]) and replay(B["load_bearing"])
        ok = (not interf) and pres_diff and rep         # noninterference holds AND presentation genuinely changed AND replays
        clean_ok &= ok
        rows.append({"fx": fx["id"], "decision": d["decision"], "reason": d["reason_code"],
                     "lb_A": lb_hash(A["load_bearing"]), "lb_B": lb_hash(B["load_bearing"]),
                     "lb_match": lb_match, "presentation_differs": pres_diff, "replay_ok": rep,
                     "text_A": A["rendered_text"][:40], "text_B": B["rendered_text"],
                     "NONINTERFERENCE": ok})

    # teeth: mutants MUST be detected as interference (or replay-fail)
    mut_fx = decide({"id": "M", "has_receipt": True, "warrant": False, "forbidden": False})  # a HOLD case
    base = render_default(mut_fx)
    mutants = {"MUTANT_TRUNCATE_REASON": mutant_truncate_reason,
               "MUTANT_DROP_INPUT": mutant_drop_input,
               "MUTANT_FLIP_DECISION": mutant_flip_decision}
    mrows, teeth_ok = [], True
    for name, fn in mutants.items():
        m = fn(mut_fx)
        interf, lb_match, _ = noninterference(base, m)
        rep_ok = replay(m["load_bearing"])
        detected = interf or (not rep_ok)               # interference OR broken replay = caught
        teeth_ok &= detected
        mrows.append({"mutant": name, "interference_detected": interf, "replay_ok": rep_ok, "DETECTED": detected})

    passed = clean_ok and teeth_ok
    print("=== STYLE_NONINTERFERENCE_V0 ===")
    print("  -- CLEAN: Default vs Concise on frozen fixtures (decision-bearing must match, prose must differ) --")
    for r in rows:
        print(f"  {r['fx']}  {r['decision']:7}/{r['reason']:22} lb_A={r['lb_A']} lb_B={r['lb_B']} "
              f"match={r['lb_match']} presΔ={r['presentation_differs']} replay={r['replay_ok']} -> {'PASS' if r['NONINTERFERENCE'] else 'FAIL'}")
        print(f"       A:{r['text_A']!r:44} B:{r['text_B']!r}")
    print("\n  -- TEETH: mutants leaking style into decision-bearing fields MUST be detected --")
    for m in mrows:
        print(f"  {m['mutant']:24} interference={m['interference_detected']} replay_ok={m['replay_ok']} -> {'DETECTED' if m['DETECTED'] else 'MISSED (BROKEN)'}")
    print(f"\n  CLEAN_NONINTERFERENCE={clean_ok} · MUTANTS_ALL_DETECTED={teeth_ok}")
    print(f"  STYLE_NONINTERFERENCE_V0 = {'SURVIVED_DEFINED_ATTACK_SET' if passed else 'FALSIFIED'}")
    print("  Decision_Concise = Decision_Default · ΔOutputStyle≠0 ∧ ΔDecision=0 · authority=false · canon=false · ledger_effect=none")

    receipt = {"receipt": "STYLE_NONINTERFERENCE_V0",
               "invariant": "Style(x)=Style'(x) => Decision(x)=Decision(x)  [K0a at render layer]",
               "compared": "LoadBearingReceiptBody (decision+reason+inputs), NOT full serialized bytes",
               "allowed_to_differ": ["rendered_text", "token_count", "presentation_density"],
               "clean": rows, "clean_noninterference": clean_ok,
               "mutants": mrows, "mutants_all_detected": teeth_ok,
               "RESULT": "SURVIVED_DEFINED_ATTACK_SET" if passed else "FALSIFIED",
               "SelfPassed": True, "PeerAdversaryValidated": False,
               "authority": False, "canon": False, "ledger_effect": "none"}
    body = json.dumps(receipt, indent=2)
    receipt["receipt_sha16"] = hashlib.sha256(body.encode()).hexdigest()[:16]
    (OUT / "style_noninterference_v0_receipt.json").write_text(json.dumps(receipt, indent=2))
    print(f"  receipt: her_run/style_noninterference_v0_receipt.json sha16={receipt['receipt_sha16']}")

if __name__ == "__main__":
    main()
