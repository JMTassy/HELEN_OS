"""FABLE_LEAN_V0 — token-savings measurement (LIVE). authority=false · canon=false · ledger_effect=none.
NON-SOVEREIGN. Measures real credit savings of adaptive lazy spawning vs a fixed-5 baseline.

Method (honest counterfactual): for each task, run A+B (mandatory scouts) live, derive gate signals from THEIR
output, then run C,D,E live too — but tag each specialist SPAWNED (gate needed it) or SKIPPED (gate did not).
  baseline_total = tokens(A,B,C,D,E)              # always-5
  lean_total     = tokens(A,B + gate-spawned)     # adaptive
  savings        = tokens(gate-skipped specialists)
Skipped roles are run HERE only to price the counterfactual; in production they are never run.
Fail-open to cognition: an undetermined signal => SPAWN (safe — Gamma_C != Gamma_A, more cognition touches no authority).
enable_thinking:false + hard timeout so no role truncates into <think>. No auto budget rescue.
"""
import json, re, signal, time, urllib.request, pathlib

URL = "http://127.0.0.1:8088/v1/chat/completions"
HERE = pathlib.Path(__file__).resolve().parent
POLICY = json.loads((HERE / "SPAWN_POLICY.json").read_text())
BUD = POLICY["budgets_tokens"]; HARD = 150
OUT = HERE / "run_measure"; OUT.mkdir(exist_ok=True)
signal.signal(signal.SIGALRM, lambda *a: (_ for _ in ()).throw(TimeoutError()))

def ask(system, user, max_tokens):
    body = json.dumps({"messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
                       "temperature": 0, "max_tokens": max_tokens, "stream": False,
                       "chat_template_kwargs": {"enable_thinking": False}}).encode()
    t = time.time()
    try:
        signal.alarm(HARD)
        j = json.loads(urllib.request.urlopen(urllib.request.Request(URL, body, {"Content-Type": "application/json"}), timeout=HARD).read())
        signal.alarm(0)
        u = j.get("usage", {})
        return j["choices"][0]["message"]["content"], u.get("completion_tokens", 0), round(time.time()-t, 1), "OK"
    except Exception as e:
        signal.alarm(0); return f"__ERROR__ {e}", 0, round(time.time()-t, 1), "ERROR"

def extract(t):
    t = re.sub(r"<think>.*?</think>", " ", t or "", flags=re.S | re.I)
    for m in re.finditer(r"\{", t):
        d = 0
        for j in range(m.start(), len(t)):
            if t[j] == "{": d += 1
            elif t[j] == "}":
                d -= 1
                if d == 0:
                    try: return json.loads(t[m.start():j+1])
                    except Exception: pass
                    break
        else: continue
        break
    return None

BASE = ("You are a HELEN goblin (authority=false). FREE COGNITION. NO AUTHORITY MINTING. Speculation must be typed. "
        "NO DIRECT STATE EFFECT. Emit ONE strict JSON packet and nothing else. /no_think")
SCOUT_SCHEMA = ('{"ID":"","CLAIM_CLASS":"OBSERVED|INFERRED|PROPOSAL|UNKNOWN","FINDINGS":[],"NOVEL":[],"ROOTS":[],'
                '"FALSIFIERS":[],"RISKS":[],"NEXT_TEST":"","signals":{"buildable":false,"empirical_testable":false,"promotion_or_risk":false}}')
SPEC_SCHEMA = ('{"ID":"","CLAIM_CLASS":"OBSERVED|INFERRED|PROPOSAL|UNKNOWN","FINDINGS":[],"NOVEL":[],"ROOTS":[],'
               '"FALSIFIERS":[],"RISKS":[],"NEXT_TEST":""}')
ROLE_SYS = {
 "A_ARCHITECT": "Role: ARCHITECT. Find hidden structure, decompositions, invariants, interfaces. "
                "In signals: buildable=is there an implementable construction? empirical_testable=is there a testable empirical claim? promotion_or_risk=is there an authority surface or high-impact failure mode?",
 "B_FALSIFIER": "Role: FALSIFIER. Try to destroy the claim: counterexamples, hidden assumptions, laundering. "
                "In signals: buildable/empirical_testable/promotion_or_risk as your honest assessment of the task.",
 "C_BUILDER": "Role: BUILDER. Propose the smallest thing to actually build to test this.",
 "D_EXPERIMENTER": "Role: EXPERIMENTER. Turn claims into H -> experiment -> observable -> threshold -> falsifier.",
 "E_ADVERSARY": "Role: ADVERSARY. Attack provenance, independence, scope, authority boundaries; show how it could look falsely proven.",
}

TASKS = [
 "Make Authority(T(x)) <= Authority(x) executable as one seam with a bypass mutant.",
 "Is 'HELEN is a legitimacy-preserving cognition system' a good one-line positioning?",
 "Design an experiment to test whether 5 isolated goblins earn more knowledge than 1.",
]

def run_role(role, task):
    scout = role in ("A_ARCHITECT", "B_FALSIFIER")
    schema = SCOUT_SCHEMA if scout else SPEC_SCHEMA
    sysmsg = BASE + " " + ROLE_SYS[role] + " Packet schema: " + schema
    raw, tok, secs, status = ask(sysmsg, f"TASK: {task}", BUD[role])
    pkt = extract(raw)
    complete = bool(isinstance(pkt, dict) and pkt.get("NOVEL") and pkt.get("NEXT_TEST"))
    sig = (pkt or {}).get("signals", {}) if scout else {}
    return {"role": role, "status": status, "completion_tokens": tok, "secs": secs,
            "complete": complete, "signals": sig, "packet": pkt}

def gate(scoutA, scoutB):
    keys = POLICY["gate_signal_keys"]
    def val(s, k):
        v = s.get("signals", {}).get(k)
        return True if v is None else bool(v)   # fail-open to cognition on undetermined
    agg = {k: (val(scoutA, k) or val(scoutB, k)) for k in keys}
    return {"C_BUILDER": agg["buildable"], "D_EXPERIMENTER": agg["empirical_testable"],
            "E_ADVERSARY": agg["promotion_or_risk"]}, agg

def main():
    results = []
    for task in TASKS:
        A = run_role("A_ARCHITECT", task); B = run_role("B_FALSIFIER", task)
        need, agg = gate(A, B)
        specs = {r: run_role(r, task) for r in ("C_BUILDER", "D_EXPERIMENTER", "E_ADVERSARY")}
        common = A["completion_tokens"] + B["completion_tokens"]
        baseline = common + sum(specs[r]["completion_tokens"] for r in specs)
        spawned = [r for r in specs if need[r]]; skipped = [r for r in specs if not need[r]]
        lean = common + sum(specs[r]["completion_tokens"] for r in spawned)
        saved = sum(specs[r]["completion_tokens"] for r in skipped)
        row = {"task": task, "gate_signals": agg, "spawned": spawned, "skipped": skipped,
               "tokens": {"A": A["completion_tokens"], "B": B["completion_tokens"],
                          "C": specs["C_BUILDER"]["completion_tokens"], "D": specs["D_EXPERIMENTER"]["completion_tokens"],
                          "E": specs["E_ADVERSARY"]["completion_tokens"]},
               "baseline_total": baseline, "lean_total": lean, "saved_tokens": saved,
               "savings_pct": round(100*saved/baseline, 1) if baseline else 0.0,
               "roles_run_lean": 2+len(spawned), "roles_run_baseline": 5,
               "statuses": {r: (A,B,*specs.values())[i]["status"] for i, r in enumerate(["A","B","C","D","E"])}}
        results.append(row)
        print(f"TASK: {task[:60]}")
        print(f"  signals={agg} spawned={spawned} skipped={skipped}")
        print(f"  baseline={baseline} lean={lean} saved={saved} ({row['savings_pct']}%) roles {row['roles_run_lean']}/5")
    agg_base = sum(r["baseline_total"] for r in results); agg_lean = sum(r["lean_total"] for r in results)
    agg_saved = agg_base - agg_lean
    summary = {"n_tasks": len(results), "baseline_tokens": agg_base, "lean_tokens": agg_lean,
               "saved_tokens": agg_saved, "savings_pct": round(100*agg_saved/agg_base, 1) if agg_base else 0.0,
               "roles_run_lean": sum(r["roles_run_lean"] for r in results), "roles_run_baseline": 5*len(results),
               "per_task": results, "authority": False, "canon": False, "ledger_effect": "none",
               "note": "Skipped roles were run only to price the counterfactual; production never runs them. temp0, enable_thinking:false, no auto-rescue."}
    (OUT / "savings_report.json").write_text(json.dumps(summary, indent=2))
    print(f"\n=== AGGREGATE === baseline={agg_base} lean={agg_lean} saved={agg_saved} tok "
          f"({summary['savings_pct']}%) · roles {summary['roles_run_lean']}/{summary['roles_run_baseline']}")
    print("report:", OUT / "savings_report.json"); print("DONE_MEASURE")

if __name__ == "__main__":
    main()
