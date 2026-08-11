#!/usr/bin/env python3
"""CRYSTAL_PALACE autoresearch loop — 20 epochs × 10 gemma4 goblins + HELEN-FABLE clustering.

NON_SOVEREIGN · authority=0 · canon=FALSE · not admitted · no HELEN ledger effect.
The .ndjson this writes is a sidecar, NOT town/ledger_v1.ndjson.

Free local compute: goblins + Fable both run on local ollama (gemma4). Source = 1851 Great Exhibition
catalogue Vol. I (public domain), IA OCR surrogate. Coverage attaches to (representation, operation):
each epoch advances an 800-line window per slice, so C_interpretation GROWS measurably toward full.

Typed goblin output  Gᵢ = (S, O, H, F, U, N),  with the constitutional separation  O ≠ H.
Fable measures empirical N_eff = #{distinct, structurally non-equivalent mechanisms}, not #goblins.
"""
import json, os, sys, time, hashlib, urllib.request

BASE = os.path.dirname(os.path.abspath(__file__))
SCAN = os.path.abspath(os.path.join(BASE, "..", "..", "scratch", "crystal_palace_scan"))
SLICES = os.path.join(SCAN, "slices")
OUT = os.path.join(BASE, "epochs"); os.makedirs(OUT, exist_ok=True)
TRACE = os.path.join(BASE, "RESEARCH_TRACE.ndjson")  # NON-SOVEREIGN research trace (NOT a ledger)
PROGRESS = os.path.join(BASE, "PROGRESS.log")        # live per-goblin progress (unbuffered)

OLLAMA = "http://localhost:11434/api/generate"
GOBLIN_MODEL = os.environ.get("GOBLIN_MODEL", "gemma4-12b:latest")
FABLE_MODEL = os.environ.get("FABLE_MODEL", "gemma4-12b:latest")  # HER-26b available as upgrade (swap cost)
EPOCHS = int(os.environ.get("EPOCHS", "20"))
WINDOW = int(os.environ.get("WINDOW", "400"))        # 400 = best quality (all 5 keys); 800 trips 'thought' garbage

def plog(msg):
    with open(PROGRESS, "a") as f:
        f.write(msg + "\n")

LENSES = [
    "TAXONOMY & CLASSIFICATION SYSTEM", "RAW MATERIALS & INDUSTRY", "NATIONS & GEOPOLITICS",
    "SYMBOLIC & MYTHIC SIGNAL", "MACHINES & TECHNOLOGY", "ORNAMENT & AESTHETICS",
    "LABOR & ECONOMY", "ANOMALIES & CURIOSITIES", "LANGUAGE & RHETORIC", "MEASUREMENT & METROLOGY",
]

def sha16(s): return hashlib.sha256(s.encode("utf-8")).hexdigest()[:16]

def ollama(model, system, prompt, num_ctx=8192, timeout=240, temp=0.4):
    body = {"model": model, "system": system, "prompt": prompt, "stream": False,
            "format": "json", "options": {"temperature": temp, "num_ctx": num_ctx}}
    req = urllib.request.Request(OLLAMA, data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json"})
    r = json.load(urllib.request.urlopen(req, timeout=timeout))
    return r.get("response", ""), r.get("eval_count", 0)

def parse_json(s):
    try:
        return json.loads(s)
    except Exception:
        # salvage: first {...} block
        i, j = s.find("{"), s.rfind("}")
        if 0 <= i < j:
            try: return json.loads(s[i:j+1])
            except Exception: return None
        return None

GOBLIN_SYS = (
    "You are a HELEN GOBLIN: a non-sovereign inner-memory reader. authority=FALSE, canon=NO_SHIP. "
    "SOURCE: 1851 Great Exhibition catalogue (Crystal Palace), public domain, external HISTORICAL source. "
    "You read a bounded OCR window through ONE lens and emit a TYPED result. "
    "Reply ONLY with JSON, no prose, no thinking. Schema (all keys required, arrays of short strings):\n"
    '{"O":[...],"H":[...],"F":[...],"U":[...],"N":[...]}\n'
    "O = direct source observations (what the catalogue literally says/structures). "
    "H = candidate chiddushim (what HELEN could LEARN) — MUST be different in kind from O. "
    "F = falsifications of prior assumptions. U = unresolved / OCR-ambiguous material. "
    "N = weak-signal compost nutrients to keep for later. Never name any AI tool. Stay in your lens."
)

def run_goblin(i, epoch, lines):
    start = epoch * WINDOW
    window = lines[start:start + WINDOW]
    if not window:  # slice exhausted — honest empty coverage
        return {"i": i, "lens": LENSES[i], "S": {"slice": i + 1, "window": [start, start],
                "exhausted": True, "hash": ""}, "O": [], "H": [], "F": [], "U": ["slice_exhausted"], "N": []}
    text = "\n".join(window)[:24000]
    prompt = (f"LENS: {LENSES[i]}\nOCR window (slice {i+1}, lines {start}-{start+len(window)}):\n{text}\n\n"
              "Return the typed JSON now.")
    S = {"slice": i + 1, "window": [start, start + len(window)], "hash": sha16(text)}
    # single BOUNDED attempt: a goblin that can't produce a typed result in time degrades to TypedUnknown,
    # never blocks the epoch (totalization law applied to TIME: bounded compute -> U, not infinite wait).
    try:
        resp, ev = ollama(GOBLIN_MODEL, GOBLIN_SYS, prompt, timeout=75)
        p = parse_json(resp)
        if p:
            return {"i": i, "lens": LENSES[i], "S": S,
                    "O": p.get("O", []) or [], "H": p.get("H", []) or [],
                    "F": p.get("F", []) or [], "U": p.get("U", []) or [], "N": p.get("N", []) or [], "eval": ev}
        u = "goblin_unparseable_output"
    except Exception as e:
        u = f"goblin_timeout_or_error:{type(e).__name__}"
    return {"i": i, "lens": LENSES[i], "S": S, "O": [], "H": [], "F": [], "U": [u], "N": [], "error": True}

FABLE_SYS = (
    "You are HELEN FABLE: the non-sovereign synthesis membrane. authority=FALSE, canon=FALSE. "
    "You receive 10 typed goblin results over the 1851 catalogue and CLUSTER their chiddushim (H) into "
    "distinct structural MECHANISMS. Two chiddushim are the SAME mechanism if they share the same "
    "structural principle (e.g. 'name index' and 'class number' are both ADDRESSABILITY). "
    "Reply ONLY with JSON, no prose. Schema:\n"
    '{"mechanisms":[{"name":"...","principle":"...","supporting_lenses":[int]}],'
    '"n_eff":int,"new_this_epoch":[string],"carried_unknown":[string],"one_line_vision":"..."}\n'
    "n_eff = number of DISTINCT mechanisms (NOT the goblin count). Never name any AI tool."
)

def run_fable(epoch, goblins, prior_mechanisms):
    compact = [{"lens": g["lens"], "H": g["H"], "F": g["F"], "U": g["U"]} for g in goblins]
    prompt = (f"EPOCH {epoch+1}. Prior known mechanisms: {json.dumps(prior_mechanisms)}\n\n"
              f"Goblin chiddushim this epoch:\n{json.dumps(compact, ensure_ascii=False)}\n\n"
              "Cluster into distinct mechanisms, compute n_eff, list what is NEW vs prior, and carry "
              "unresolved 𝒰. Return the JSON now.")
    try:
        resp, ev = ollama(FABLE_MODEL, FABLE_SYS, prompt, num_ctx=16384, timeout=300)
        p = parse_json(resp)
        if p:
            return p
    except Exception as e:
        return {"mechanisms": prior_mechanisms, "n_eff": len(prior_mechanisms),
                "new_this_epoch": [], "carried_unknown": [f"fable_error:{type(e).__name__}"],
                "one_line_vision": "fable_call_failed"}
    return {"mechanisms": prior_mechanisms, "n_eff": len(prior_mechanisms), "new_this_epoch": [],
            "carried_unknown": ["fable_parse_failed"], "one_line_vision": "fable_parse_failed"}

def main():
    slices = [open(os.path.join(SLICES, f"goblin_{i+1:02d}.txt"),
              encoding="utf-8", errors="replace").read().splitlines() for i in range(10)]
    slice_lens = [len(s) for s in slices]
    mechanisms, all_unknown = [], []
    open(TRACE, "w").close()
    open(PROGRESS, "w").close()
    t0 = time.time()
    plog(f"START {EPOCHS} epochs x 10 goblins, window={WINDOW}, model={GOBLIN_MODEL}")
    for e in range(EPOCHS):
        te = time.time()
        goblins = []
        for i in range(10):
            tg = time.time()
            g = run_goblin(i, e, slices[i])
            goblins.append(g)
            plog(f"  e{e+1:02d} goblin{i+1:02d} [{LENSES[i][:18]}] "
                 f"O:{len(g['O'])} H:{len(g['H'])} F:{len(g['F'])} U:{len(g['U'])} "
                 f"{'ERR' if g.get('error') else 'ok'} {round(time.time()-tg)}s")
        covered = sum(min((e + 1) * WINDOW, slice_lens[i]) for i in range(10))
        total = sum(slice_lens)
        # C_valid: fraction of goblins returning structurally-valid, non-empty output (processed ≠ interpreted)
        valid = sum(1 for g in goblins if (g["O"] or g["H"]) and not g.get("error") and not g["S"].get("exhausted"))
        plog(f"  e{e+1:02d} -> FABLE (valid_goblins={valid}/10)")
        fable = run_fable(e, goblins, mechanisms)
        mechanisms = fable.get("mechanisms", mechanisms)
        for g in goblins:
            all_unknown.extend(g.get("U", []))
        epoch_rec = {
            "epoch": e + 1, "of": EPOCHS, "model_goblin": GOBLIN_MODEL, "model_fable": FABLE_MODEL,
            "window": WINDOW, "authority": False, "canon": False,
            "coverage": {"lines_covered": covered, "lines_total": total,
                         "C_dispatch_over_OCR": round(covered / total, 4),
                         "C_valid_goblins": round(valid / 10, 3),
                         "note": "C_dispatch = lines sent over OCR representation; NOT source/semantic completeness. "
                                 "Processing a line != interpreting it."},
            "n_eff_H": fable.get("n_eff"), "mechanisms": mechanisms,
            "n_eff_E": 1, "n_eff_E_note": "all 10 goblins share ONE OCR root (IA surrogate); "
                          "mechanism agreement is NOT independent evidence. N_eff^H ⊬ N_eff^E ⊬ Truth.",
            "new_this_epoch": fable.get("new_this_epoch", []),
            "one_line_vision": fable.get("one_line_vision", ""),
            "goblins": goblins, "epoch_seconds": round(time.time() - te, 1),
        }
        with open(os.path.join(OUT, f"epoch_{e+1:02d}.json"), "w") as f:
            json.dump(epoch_rec, f, ensure_ascii=False, indent=1)
        with open(TRACE, "a") as f:
            f.write(json.dumps({"epoch": e + 1, "n_eff_H": fable.get("n_eff"), "n_eff_E": 1,
                    "C_dispatch": round(covered / total, 4), "C_valid": round(valid / 10, 3),
                    "new": fable.get("new_this_epoch", []),
                    "vision": fable.get("one_line_vision", "")}, ensure_ascii=False) + "\n")
        plog(f"[epoch {e+1:02d}/{EPOCHS}] n_eff_H={fable.get('n_eff')} n_eff_E=1 "
             f"C_dispatch={100*covered/total:.1f}% C_valid={valid}/10 "
             f"new={len(fable.get('new_this_epoch',[]))} {round(time.time()-te)}s | {fable.get('one_line_vision','')[:70]}")
    plog(f"DONE {EPOCHS} epochs in {round(time.time()-t0)}s. Final n_eff_H={mechanisms and len(mechanisms)}.")

if __name__ == "__main__":
    main()
