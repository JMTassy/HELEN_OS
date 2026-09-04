"""STEP 2 — VOICE dataset builder (HAL-gated). NON_SOVEREIGN. authority=false.
Turns JMT-authored voice excerpts into instruction->completion pairs for a VOICE LoRA.
FAIL-CLOSED PII scrub + re-scan: a row with a surviving leak is DROPPED, never shipped.
Weights ⊬ receipt: this teaches STYLE only. Facts stay in governed RAG with citations.

Input  : raw_excerpts.jsonl  rows = {"text":..., "source_file_id":..., "kind":"linkedin|manifesto|talk|note"}
Output : voice_dataset.train.jsonl · voice_dataset.eval.jsonl · build_report.json
Run    : python3 build_voice_dataset.py --in raw_excerpts.jsonl   (or --demo)
"""
import json, re, argparse, hashlib
from pathlib import Path

# ---- HARD EXCLUSION: kinds/sources that must NEVER become training data ----
FORBIDDEN_KINDS = {"invoice","admin","financial","client_deck","rh","student","third_party","other_entity"}

# ---- PII patterns (fail-closed: detect -> redact -> RE-SCAN -> drop if survives) ----
PII = {
 "EMAIL": re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b"),
 "IBAN":  re.compile(r"\b[A-Z]{2}\d{2}[A-Z0-9]{10,32}\b"),
 "PHONE": re.compile(r"(?:\+33|0033|0)\s?[1-9](?:[\s.-]?\d{2}){4}\b"),
 "CARD":  re.compile(r"\b(?:\d[ -]?){13,19}\b"),
 "SIREN": re.compile(r"\b\d{9}\b|\b\d{14}\b"),
 "HANDLE":re.compile(r"(?<!\w)@[A-Za-z0-9_.]{2,}"),
}
INSTRUCTION = {
 "linkedin":  "Write a LinkedIn post in JMT's voice on this theme:",
 "manifesto": "State this idea as JMT would, in his manifesto voice:",
 "talk":      "Deliver this point as JMT would on stage:",
 "note":      "Express this in JMT's voice:",
}
SYSTEM = ("You write in the voice of JMT — Polytechnique-precise, editorial, confident, "
          "concrete over abstract, receipts over claims, warm but sharp. Voice only; you do "
          "not assert facts you cannot cite.")

def scrub(text, name_blocklist):
    redactions = []
    for name in sorted(name_blocklist, key=len, reverse=True):
        if name and name.lower() in text.lower():
            text = re.sub(re.escape(name), "[NAME]", text, flags=re.IGNORECASE); redactions.append("NAME")
    for tag, rx in PII.items():
        if rx.search(text): text = rx.sub(f"[{tag}]", text); redactions.append(tag)
    return text, redactions

def rescan_clean(text):
    # fail-closed: after scrub NOTHING sensitive may remain
    for tag in ("EMAIL","IBAN","PHONE","CARD"):
        if PII[tag].search(text): return False, tag
    return True, None

def topic_of(text):  # a light theme hint from the first clause (kept generic, no PII)
    first = re.split(r"[.!?\n]", text.strip())[0]
    return (first[:80] + "…") if len(first) > 80 else first

def build(rows, name_blocklist):
    kept, dropped = [], []
    for i, r in enumerate(rows):
        kind = (r.get("kind") or "note").lower()
        if kind in FORBIDDEN_KINDS:
            dropped.append({"i":i,"reason":f"FORBIDDEN_KIND:{kind}","src":r.get("source_file_id")}); continue
        raw = (r.get("text") or "").strip()
        if len(raw) < 40:
            dropped.append({"i":i,"reason":"TOO_SHORT","src":r.get("source_file_id")}); continue
        scrubbed, red = scrub(raw, name_blocklist)
        ok, leak = rescan_clean(scrubbed)
        if not ok:
            dropped.append({"i":i,"reason":f"LEAK_SURVIVED:{leak}","src":r.get("source_file_id")}); continue
        instr = f"{INSTRUCTION.get(kind, INSTRUCTION['note'])} {topic_of(scrubbed)}"
        kept.append({"messages":[{"role":"system","content":SYSTEM},
                                 {"role":"user","content":instr},
                                 {"role":"assistant","content":scrubbed}],
                     "meta":{"source_file_id":r.get("source_file_id","UNKNOWN"),
                             "kind":kind,"pii_scrubbed":True,"redactions":sorted(set(red))}})
    return kept, dropped

def split(kept):  # deterministic 90/10 by content hash (no RNG)
    tr, ev = [], []
    for row in kept:
        h = int(hashlib.sha256(row["messages"][2]["content"].encode()).hexdigest(), 16)
        (ev if h % 10 == 0 else tr).append(row)
    return tr, ev

DEMO = [
 {"kind":"linkedin","source_file_id":"demo_1","text":"AI made production free. So I sell what it never touched: 25 years of receipts, a voice, and the people who answer the phone. Reach me at jm@uzik.com or @jmtassy."},
 {"kind":"manifesto","source_file_id":"demo_2","text":"In 2000 I bet creative and technical would fuse before anyone was ready. The AI age is that bet at maximum amplitude. My IBAN FR7630006000011234567890189 is not the point — the method is."},
 {"kind":"client_deck","source_file_id":"demo_3","text":"CONFIDENTIAL Google campaign metrics: 9M impressions, budget details..."},
]

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp"); ap.add_argument("--demo", action="store_true")
    ap.add_argument("--names", default="", help="comma-separated name blocklist to pseudonymize")
    a = ap.parse_args()
    blocklist = [n.strip() for n in a.names.split(",") if n.strip()]
    rows = DEMO if a.demo else [json.loads(l) for l in open(a.inp) if l.strip()]
    kept, dropped = build(rows, blocklist)
    tr, ev = split(kept)
    if not a.demo:
        Path("voice_dataset.train.jsonl").write_text("".join(json.dumps(r,ensure_ascii=False)+"\n" for r in tr))
        Path("voice_dataset.eval.jsonl").write_text("".join(json.dumps(r,ensure_ascii=False)+"\n" for r in ev))
    report = {"in":len(rows),"kept":len(kept),"dropped":len(dropped),"train":len(tr),"eval":len(ev),
              "drop_reasons":dropped}
    print(json.dumps(report, indent=2, ensure_ascii=False))
    if a.demo:
        print("\n--- sample kept row (scrubbed) ---")
        print(json.dumps(kept[0], indent=2, ensure_ascii=False) if kept else "(none)")
