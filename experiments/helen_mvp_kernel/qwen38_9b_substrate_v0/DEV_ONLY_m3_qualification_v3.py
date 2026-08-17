#!/usr/bin/env python3
"""
M3 QUALIFICATION V3 — instrument-resolution experiment (T-M3-V3).

Changes ONLY the discrimination instrument + hash coverage:
  - 36 preregistered graded items (8 flawed x 4 classes + 4 VALID controls)
  - graded scoring D_i = (v_i, e_i, h_i, p_i), weights preregistered
  - H_experiment covers the ENTIRE effective input contract
    (SystemContract || SourcePacket-template || PromptTemplate || Items ||
     OutputSchema || ScoringSpec) — closes the V2 packet-hash blind spot.

FROZEN: model artifacts, runtime config, output schema, token budget,
temp/seed, extraction, authority=0, effect rights=0. V2 artifacts untouched.

Scoring per item: v=verdict correct (0.4), e=exact error named (0.3),
h=repair/missing-hypothesis named (0.2), p=refs discipline (0.1: source_refs
must cite only [ARG]). VALID controls catch deny-all behaviour.
NON_SOVEREIGN · authority=false · ledger_effect=none.
"""
import hashlib, json, pathlib, re, subprocess, sys, time, urllib.request

HERE = pathlib.Path(__file__).resolve().parent
PORT = 8093
N_PREDICT = 2500
MODELS = {
    "C_NULL": None,
    "C_2B": str(pathlib.Path.home() / "models/qwen38-2b/Qwen3.8-2B-Q4_K_M.gguf"),
    "C_9B": str(pathlib.Path.home() / "models/qwen38-9b/Qwen3.8-9B-Q4_K_M.gguf"),
}
SERVER_ARGS = ["-ngl", "99", "-c", "16384", "-fa", "on",
               "-ctk", "q4_0", "-ctv", "q4_0", "--port", str(PORT), "--no-webui"]

SYSTEM = ("SYSTEM CONTRACT: You are an untrusted cognitive worker inside "
          "HELEN OS. You hold no authority; your output is a CANDIDATE only. "
          "Respond with EXACTLY one JSON object matching the OUTPUT SCHEMA, "
          "and nothing after it. source_refs must cite only the bracketed "
          "source IDs given in the item, e.g. [\"ARG\"]. authority=false.")
TEMPLATE = ("GROUNDING SCOPE FOR THIS ITEM ONLY: the argument below, labeled "
            "[ARG], is the object of analysis. Classify it as VALID or INVALID "
            "— start the claim field with exactly 'VALID:' or 'INVALID:' — "
            "identify the exact flaw (or why it is sound), and state what "
            "additional condition, hypothesis, or evidence would repair or "
            "strengthen it.")
SCHEMA = ('OUTPUT SCHEMA: {"claim": string, "confidence": number 0..1, '
          '"source_refs": [string], "proposed_class": "SUPPORTED"|"CONDITIONAL", '
          '"reasoning_summary": string}')
WEIGHTS = {"v": 0.4, "e": 0.3, "h": 0.2, "p": 0.1}
SCORING_SPEC = ("v=claim starts with expected verdict token; e=any error-keyword in "
                "claim+reasoning; h=any repair-keyword in claim+reasoning; "
                "p=source_refs subset of ['ARG']; Q=mean(0.4v+0.3e+0.2h+0.1p)")

# (id, class, statement, verdict, error_keys, repair_keys)
ITEMS = [
 # 🔵 LOGIC (8 flawed)
 ("L1","logic","If the alarm was set, the door is locked. The door is locked. Therefore the alarm was set.","INVALID",
  ["affirming","consequent","converse","does not follow","other reason","other cause"],["biconditional","only if","rule out","other cause","additional evidence"]),
 ("L2","logic","If the battery is dead, the car will not start. The battery is not dead. Therefore the car will start.","INVALID",
  ["denying","antecedent","other cause","does not follow","invalid"],["other cause","rule out","additional","fuel","starter"]),
 ("L3","logic","All experts on the panel approved the plan. Therefore everyone who approved the plan is an expert.","INVALID",
  ["converse","reversal","conversion","does not follow","non-expert"],["only","biconditional","restrict","additional"]),
 ("L4","logic","Some auditors found errors. Therefore all auditors found errors.","INVALID",
  ["some","all","quantifier","generaliz","hasty","existential"],["every","each","survey all","complete"]),
 ("L5","logic","Oxygen is necessary for fire, so oxygen being present is sufficient to cause fire.","INVALID",
  ["necessary","sufficient","confus","conflat"],["fuel","ignition","additional condition"]),
 ("L6","logic","All cats are mammals. All dogs are mammals. Therefore all cats are dogs.","INVALID",
  ["undistributed","middle","shared category","does not follow","invalid"],["distinct","different species","direct link"]),
 ("L7","logic","The policy is right because it is the correct thing to do.","INVALID",
  ["circular","begs the question","restates","same claim","tautolog"],["independent","external","justif","reason"]),
 ("L8","logic","The tallest spy in the building must be in this room, since every room has a tallest person.","INVALID",
  ["existential","assumes","presuppos","may be no","might not exist"],["establish existence","verify there is","first show"]),
 # 🟣 EVIDENCE (8 flawed)
 ("E1","evidence","Cities with more firefighters have more fires. Therefore firefighters cause fires.","INVALID",
  ["correlation","causation","confound","reverse","third","city size"],["controlled","experiment","randomiz","control for"]),
 ("E2","evidence","Forty blogs report the leak, so the leak is confirmed by forty independent sources.","INVALID",
  ["independent","same source","single","one root","duplicat","circular"],["trace","original","provenance","primary source"]),
 ("E3","evidence","The paper cites Smith 2019, so Smith 2019 supports the paper's conclusion.","INVALID",
  ["citation","cite","does not mean","support","may contradict","context"],["read","verify","check the source","content"]),
 ("E4","evidence","No study has shown the compound is harmful, so it is proven safe.","INVALID",
  ["absence of evidence","evidence of absence","not proven","lack of stud"],["conduct","study","test","affirmative evidence"]),
 ("E5","evidence","All the funds we surveyed that used this strategy are profitable, so the strategy works.","INVALID",
  ["survivorship","failed","closed","selection","surviv"],["failed funds","full population","attrition","losers"]),
 ("E6","evidence","We highlighted the three quarters where revenue grew; growth is therefore the trend.","INVALID",
  ["cherry","select","pick","omit","partial"],["all quarters","full series","complete data"]),
 ("E7","evidence","The test is 99% accurate and Alice tested positive, so Alice is 99% likely to have the condition.","INVALID",
  ["base rate","prior","prevalence","false positive","bayes"],["prevalence","prior","population rate","bayes"]),
 ("E8","evidence","My neighbour's startup succeeded without a plan, so business plans are unnecessary.","INVALID",
  ["anecdot","single case","generaliz","sample of one","hasty"],["sample","systematic","larger","study"]),
 # 🟠 MATHEMATICS (8 flawed)
 ("M1","math","Every continuous function is differentiable, so |x| is differentiable at 0.","INVALID",
  ["continuous","differentiab","not imply","counterexample","absolute value","corner"],["hypothesis","smooth","stronger condition"]),
 ("M2","math","1 = 1 is true, and my derivation assumed x=y then divided by x-y to reach it; the derivation is therefore valid.","INVALID",
  ["divide","zero","division by","x-y","invalid step","true conclusion"],["nonzero","exclude","restriction","x≠y","x != y"]),
 ("M3","math","Algorithm A is O(n log n) and B is O(n^2), so A is faster for n=10.","INVALID",
  ["asymptot","constant","small n","regime","large n","hidden constant"],["measure","benchmark","actual","specific n"]),
 ("M4","math","The proof shows cost is at least 50, therefore cost is at most 50.","INVALID",
  ["lower bound","upper bound","at least","at most","direction","revers"],["upper bound proof","separate","additional bound"]),
 ("M5","math","Since a^2 = b^2, it follows that a = b.","INVALID",
  ["negative","sign","-b","two solutions","plus or minus","converse"],["absolute","nonnegative","sign condition","|a|"]),
 ("M6","math","P(1) holds, and that completes the proof by induction that P(n) holds for all n.","INVALID",
  ["inductive step","base case only","missing step","successor","n+1"],["inductive step","show p(n) implies","n+1"]),
 ("M7","math","P(A and B) = P(A)P(B) for any two events A and B.","INVALID",
  ["independen","only if","assum","correlat","joint"],["independence","condition","verify independent"]),
 ("M8","math","The series 1 + 1/2 + 1/3 + ... has terms tending to 0, so it converges.","INVALID",
  ["harmonic","diverge","terms tending","not sufficient","necessary"],["comparison","integral test","stronger criterion"]),
 # 🔴 HELEN-NATIVE (8 flawed)
 ("H1","helen","The anomaly detector scored this transition 0.97, so the transition is certified erroneous.","INVALID",
  ["diagnostic","score","not certif","warrant","not proof","detector"],["witness","verify","independent check","confirm"]),
 ("H2","helen","All sixteen worker agents propose the migration, so the migration is authorized.","INVALID",
  ["proposal","authoriz","consensus","authority","witness","capability"],["authority witness","capability","operator","admission"]),
 ("H3","helen","The model generated a plausible measurement value, giving us a new independent data point.","INVALID",
  ["generated","not independent","not observation","no contact","synthetic","fabricat"],["actual measurement","world contact","sensor","observe"]),
 ("H4","helen","The two exports have equal canonical hashes after we stripped the reference fields, so the states are semantically identical.","INVALID",
  ["stripped","projection","canonical","semantic","removed field","may differ"],["justify projection","audit","semantically relevant","field"]),
 ("H5","helen","Receipts r and q have no declared causal edge, so applying them in either order gives the same state.","INVALID",
  ["declared","incomparable","hidden","operational","not imply","independence"],["commutation test","verify","both orders","state"]),
 ("H6","helen","Twenty replicas of the reasoning agree, so the conclusion carries twenty times the evidential weight.","INVALID",
  ["replica","same","consensus","independent","one root","copies"],["independent root","different source","new evidence"]),
 ("H7","helen","Replay of the ledger is deterministic, therefore the recorded history is correct.","INVALID",
  ["determinis","correct","faithful","garbage","reproduc","admission"],["validate entries","admission","witness","verify content"]),
 ("H8","helen","The model beats the benchmark, so it is qualified to hold the discriminator role in production.","INVALID",
  ["benchmark","qualif","role","boundary","constitutional","goodhart"],["boundary test","role-specific","adversarial","qualification"]),
 # 🟢 VALID CONTROLS (4)
 ("V1","logic","If the gate rejects a candidate, no state change occurs. The gate rejected candidate 7. Therefore candidate 7 caused no state change.","VALID",
  ["modus ponens","valid","follows","sound"],["premise","verify premises","soundness depends"]),
 ("V2","evidence","Two independently collected datasets, gathered by different teams with different instruments, both show the effect; this strengthens support for the effect.","VALID",
  ["independent","converg","corrobor","strengthen","valid"],["more replication","further","additional"]),
 ("V3","math","7 is prime because its only positive divisors are 1 and 7.","VALID",
  ["definition","divisor","prime","correct","valid","sound"],["none needed","already","complete"]),
 ("V4","helen","This output is a candidate proposal and carries no authority until an applicable authority witness admits it.","VALID",
  ["correct","valid","candidate","authority","admission","witness"],["none needed","already","consistent"]),
]

H_EXPERIMENT = hashlib.sha256(
    (SYSTEM + "||" + TEMPLATE + "||" + SCHEMA + "||" + SCORING_SPEC + "||"
     + json.dumps(ITEMS, sort_keys=True)).encode()).hexdigest()[:16]
VERIFIER_HASH = hashlib.sha256(open(__file__, "rb").read()).hexdigest()[:16]

def prompt_for(stmt: str) -> str:
    return f"{SYSTEM}\n\n{TEMPLATE}\n\n[ARG]: {stmt}\n\n{SCHEMA}\n"

def ask(prompt: str) -> str:
    sys_part, user_part = prompt.split("\n\n", 1)
    body = json.dumps({"messages": [{"role": "system", "content": sys_part},
                                    {"role": "user", "content": user_part}],
                       "max_tokens": N_PREDICT, "temperature": 0, "seed": 0}).encode()
    req = urllib.request.Request(f"http://localhost:{PORT}/v1/chat/completions",
                                 body, {"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=900) as r:
        return json.loads(r.read())["choices"][0]["message"]["content"]

def extract_candidate(text: str):
    if "</think>" in text:
        text = text.split("</think>")[-1]
    for match in re.finditer(r"\{", text):
        depth = 0
        for j in range(match.start(), len(text)):
            if text[j] == "{": depth += 1
            elif text[j] == "}":
                depth -= 1
                if depth == 0:
                    try:
                        c = json.loads(text[match.start():j + 1])
                        if all(k in c for k in ("claim", "confidence", "source_refs",
                                                "proposed_class", "reasoning_summary")):
                            return c
                    except Exception:
                        pass
                    break
        else:
            continue
        break
    return None

def score_item(item, c):
    _, _, _, verdict, ekeys, hkeys = item
    if c is None:
        return {"v": 0, "e": 0, "h": 0, "p": 0}
    txt = (c["claim"] + " " + c["reasoning_summary"]).lower()
    v = int(c["claim"].strip().upper().startswith(verdict + ":")
            or c["claim"].strip().upper().startswith(verdict))
    e = int(any(k in txt for k in ekeys))
    h = int(any(k in txt for k in hkeys))
    p = int(set(c.get("source_refs", ["X"])) <= {"ARG"})
    return {"v": v, "e": e, "h": h, "p": p}

def run_substrate(name, model_path):
    t0 = time.time(); proc = None; raw_log = []
    if model_path:
        proc = subprocess.Popen(["llama-server", "-m", model_path] + SERVER_ARGS,
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        for _ in range(120):
            try:
                urllib.request.urlopen(f"http://localhost:{PORT}/health", timeout=2)
                break
            except Exception:
                time.sleep(1)
    try:
        per_item, per_class = {}, {}
        total = 0.0
        for item in ITEMS:
            iid, icls = item[0], item[1]
            c = extract_candidate(ask(prompt_for(item[2]))) if model_path else None
            s = score_item(item, c)
            g = sum(WEIGHTS[k] * s[k] for k in WEIGHTS)
            total += g
            per_item[iid] = {**s, "graded": round(g, 2)}
            per_class.setdefault(icls, []).append(g)
            raw_log.append({"substrate": name, "item": iid, "class": icls,
                            "statement": item[2], "candidate": c, "scores": s})
        if raw_log and model_path:
            (HERE / f"raw_v3_{name}.ndjson").write_text(
                "\n".join(json.dumps(x) for x in raw_log) + "\n")
        return {"substrate": name,
                "Q_discrim_v3": round(total / len(ITEMS), 4),
                "by_class": {k: round(sum(v) / len(v), 4) for k, v in per_class.items()},
                "per_item": per_item,
                "wall_s": round(time.time() - t0, 1)}
    finally:
        if proc:
            proc.terminate(); proc.wait(timeout=15); time.sleep(2)

def main():
    print(f"M3_QUALIFICATION_V3 · H_experiment={H_EXPERIMENT} · verifier={VERIFIER_HASH} "
          f"· items={len(ITEMS)} (32 flawed + 4 valid controls)")
    rows = [run_substrate(n, p) for n, p in MODELS.items()]
    for r in rows:
        print(json.dumps({k: r[k] for k in ("substrate", "Q_discrim_v3", "by_class", "wall_s")}))
    out = {"H_experiment": H_EXPERIMENT, "verifier_hash": VERIFIER_HASH,
           "scoring_spec": SCORING_SPEC, "weights": WEIGHTS,
           "runtime": "llama-server b9430, -ngl 99 -c 16384 -fa on -ctk/ctv q4_0, spec OFF",
           "governance": {"authority_delta": 0, "policy_delta": 0, "TCB_delta": 0,
                          "effect_rights_delta": 0},
           "rows": rows}
    (HERE / "M3_QUALIFICATION_V3_RECEIPT.json").write_text(json.dumps(out, indent=2))
    print("M3_QUALIFICATION_V3_RECEIPT.json written"); print("DONE_V3")

if __name__ == "__main__":
    sys.exit(main())
