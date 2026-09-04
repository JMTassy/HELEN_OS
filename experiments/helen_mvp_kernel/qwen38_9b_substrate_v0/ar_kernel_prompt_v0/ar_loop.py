#!/usr/bin/env python3
"""
AUTORESEARCH_KERNEL_PROMPT_V0 — PULL-mode loop: 10 epochs max OR 20-min wall
cap, whichever first. One hypothesis per epoch; 7-field receipt per epoch;
everything HOLD_FOR_OPERATOR; mutable surface = prompt strategy ONLY.
Substrate: 2B (fast loop + directly tests the relayed unwitnessed claim that
the long constitution wins on the small model). Fixtures/scorer/runtime frozen
from V3. NON_SOVEREIGN · authority=false · ledger_effect=none · NO promotion.
"""
import json, pathlib, re, subprocess, sys, time, urllib.request

HERE = pathlib.Path(__file__).resolve().parent
BASE = HERE.parent
V3 = BASE / "v3"; PA = BASE / "prompt_ablation_v0"
sys.path.insert(0, str(V3))
from scorer import score_item, q_of, fixtures

RT = json.loads((V3 / "runtime_contract.json").read_text())
TEMPLATE = (V3 / "template.txt").read_text()
SCHEMA = (V3 / "output_schema.json").read_text().strip()
PORT = 8095; SAMP = RT["sampling"]
MODEL = RT["models"]["SUB_1"]  # 2B
ADAPTER = ("\n\nOUTPUT CONTRACT: Respond with EXACTLY one JSON object matching "
           "the OUTPUT SCHEMA in the user message, and nothing after it. "
           "Evaluate ONLY the CLAIM against the SOURCES given in the item; the "
           "sources are the entire world for this item. source IDs are the "
           "bracketed tokens (e.g. R1). authority=false.")
WALL_CAP = 20 * 60
K7 = (PA / "ARM_1_KERNEL7.txt").read_text()

def k7_minus(i: int) -> str:
    parts = re.split(r"(?m)^(?=\d\. )", K7)   # header + 7 law blocks
    head, laws = parts[0], parts[1:]
    kept = [l for j, l in enumerate(laws, 1) if j != i]
    return head + "".join(kept)

EPOCHS = [
    ("E01", "relayed-claim: bare baseline on 2B", (PA / "ARM_0_BASELINE.txt").read_text()),
    ("E02", "relayed-claim: kernel7 on 2B", K7),
    ("E03", "relayed-claim: long constitution on 2B", (PA / "ARM_2_LONG.txt").read_text()),
] + [(f"E{i+3:02d}", f"leave-one-law-out: K7 minus L{i}", k7_minus(i)) for i in range(1, 8)]

def user_message(fx):
    body = TEMPLATE.split("\n\n", 1)[1]
    return body.replace("{source}", fx["source"]).replace("{claim}", fx["claim"]) \
               .replace("{output_schema}", SCHEMA)

def ask(system, user):
    body = json.dumps({"messages": [{"role": "system", "content": system},
                                    {"role": "user", "content": user}],
                       "max_tokens": SAMP["max_tokens"], "temperature": 0,
                       "seed": 0}).encode()
    req = urllib.request.Request(f"http://localhost:{PORT}/v1/chat/completions",
                                 body, {"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=600) as r:
        return json.loads(r.read())["choices"][0]["message"]["content"]

def extract(text):
    if "</think>" in text:
        text = text.split("</think>")[-1]
    for m in re.finditer(r"\{", text):
        depth = 0
        for j in range(m.start(), len(text)):
            if text[j] == "{": depth += 1
            elif text[j] == "}":
                depth -= 1
                if depth == 0:
                    try:
                        c = json.loads(text[m.start():j + 1])
                        if "epistemic_class" in c:
                            return c
                    except Exception:
                        pass
                    break
        else:
            continue
        break
    return None

def main():
    t0 = time.time()
    path = str(pathlib.Path(MODEL["path"]).expanduser())
    proc = subprocess.Popen(["llama-server", "-m", path] + RT["args"]
                            + ["--port", str(PORT), "--no-webui"],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for _ in range(90):
        try:
            urllib.request.urlopen(f"http://localhost:{PORT}/health", timeout=2); break
        except Exception:
            time.sleep(1)
    fxs = fixtures()
    rows, carry = [], "none (first epoch)"
    try:
        for eid, hyp, arm_text in EPOCHS:
            if time.time() - t0 > WALL_CAP:
                rows.append({"epoch": eid, "status": "NOT_RUN_WALL_CAP"})
                continue
            te = time.time()
            system = arm_text.strip() + ADAPTER
            scores = []
            for fx in fxs:
                c = extract(ask(system, user_message(fx)))
                scores.append(score_item(fx, c))
            q = round(q_of(scores), 4)
            fmt = round(sum(s["valid"] for s in scores) / len(scores), 3)
            rec = {"epoch": eid,
                   "carry_forward": carry,
                   "hypothesis": hyp,
                   "experiment": "28 frozen V3 fixtures, 2B, temp0 seed0, arm-only delta",
                   "metric": {"Q_discrim": q, "Q_formatting": fmt,
                              "wall_s": round(time.time() - te, 1)},
                   "failure_mode": ("fmt<0.80" if fmt < 0.80 else "none observed"),
                   "keep_reject_rule": "informational only — HOLD_FOR_OPERATOR; no auto-promotion",
                   "upgrade_path": "operator reads tranche receipt; any prompt change needs its own verb"}
            rows.append(rec)
            carry = f"{eid}: Q={q}"
            (HERE / f"epoch_{eid}.json").write_text(json.dumps(rec, indent=1))
            print(json.dumps({"epoch": eid, "hyp": hyp[:40], "Q": q, "fmt": fmt,
                              "wall_s": rec["metric"]["wall_s"]}))
    finally:
        proc.terminate(); proc.wait(timeout=15)
    done = [r for r in rows if "metric" in r]
    tranche = {"tranche": "AUTORESEARCH_KERNEL_PROMPT_V0",
               "mode": "PULL · one hypothesis/epoch · HOLD_FOR_OPERATOR",
               "cap": "10 epochs or 1200s (first hit)",
               "epochs_run": len(done), "epochs": rows,
               "wall_total_s": round(time.time() - t0, 1),
               "authority": False, "canon": False, "ledger_effect": "none"}
    (HERE / "AR_TRANCHE_RECEIPT.json").write_text(json.dumps(tranche, indent=2))
    print(f"EPOCHS_RUN={len(done)}/{len(EPOCHS)} wall={tranche['wall_total_s']}s")
    print("AR_TRANCHE_RECEIPT.json written"); print("DONE_AR_LOOP")

if __name__ == "__main__":
    main()
