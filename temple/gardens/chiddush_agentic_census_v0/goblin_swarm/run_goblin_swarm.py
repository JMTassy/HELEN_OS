#!/usr/bin/env python3
"""
3-GOBLIN CHIDDUSH SWARM over the agentics corpus roots.
Each Goblin = distinct Ollama substrate + distinct extraction lens.
Output = chiddush: a novel structural distinction that turns the source into a
FALSIFIABLE HYPOTHESIS GENERATOR — never an ingested fact, never canon.
authority=false · NON_SOVEREIGN · Color WULmath compression.
"""
import json, re, time, urllib.request
from pathlib import Path

ROOT = Path(__file__).parent
ROOT.mkdir(exist_ok=True)
OLLAMA = "http://localhost:11434/api/chat"

# Compact corpus seed = the census roots (provenance-separated).
CORPUS = """AGENTICS CORPUS ROOTS (Drive census, provenance-separated):
ROOT-A self-authored HELEN/AgentX (one correlated source):
  Trust Geometry Ω=(H,Γ_H,X); Candidate→Admission→Receipt→Reducer→State is the
  ONLY state mutator; "ΔIntelligence>0 ⇏ ΔAuthority>0"; "one calculus, five
  projections" (Permissions/Agents/Memory/Epistemics/Superteams); BOT_ROSTER:
  "a fleet is not one expanding super-agent"; HAL→HER: posture attaches to the
  CLAIM not the file, dedup by content-hash not title, preserve contradictions.
ROOT-B external agentic-safety (Google Agents Companion, TRISM, safety toolkits)
  — the only genuinely independent witnesses.
ROOT-C Agentics Foundation org (POC Factory, Swarms, hackathon, courses).
Census laws: N_files⇏N_roots⇏N_independent_roots⇏N_independent_evidence⇏warrants;
A4: NoLineage ⇏ EpistemicIndependence."""

GOBLINS = [
    ("GOBLIN_1", "gemma4-12b:latest", "RECOMBINE",
     "bridge two DISTANT roots into one unexpected structural object"),
    ("GOBLIN_2", "aura-gemma4:latest", "CROSS_DOMAIN",
     "import ONE structure from math/physics/biology/economics that the corpus "
     "secretly already is, and name the mapping"),
    ("GOBLIN_3", "helen-core:latest", "INVERT",
     "find the ONE silently-collapsed assumption; invert it to expose an "
     "impossible-but-instructive object"),
]

SYS = """You are a GOBLIN in HELEN's NO-CLAIM Garden. authority=false. You do
CHIDDUSH extraction: you do NOT summarize or ingest the corpus as fact. You turn
it into a FALSIFIABLE HYPOTHESIS GENERATOR — a novel structural distinction plus
a test that could kill it. Esoteric/sharp is welcome; nothing you emit is
evidence, canon, or authority. Output ONLY one JSON object."""

SCHEMA = """Return ONLY:
{"seed_root":"<which root(s)>",
 "chiddush":"<the novel structural distinction, one sharp sentence>",
 "hypothesis":"<falsifiable generator it produces>",
 "discriminator":"<one test that could FALSIFY it>",
 "wulmath":"<<=12-token glyph/symbol compression of the chiddush>"}"""


def ollama(model, sys, user, timeout=300):
    body = json.dumps({"model": model, "stream": False, "think": False,
                       "messages": [{"role": "system", "content": sys},
                                    {"role": "user", "content": user}],
                       "options": {"temperature": 0.9, "num_predict": 500}}).encode()
    req = urllib.request.Request(OLLAMA, data=body,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        d = json.loads(r.read())
    m = d.get("message", {}) or {}
    return m.get("content") or m.get("thinking") or ""


def extract(t):
    def loads(s):
        try: return json.loads(s)
        except Exception: return json.loads(re.sub(r'\\(?!["\\/bfnrtu])', r'\\\\', s))
    s = t.find("{")
    while s != -1:
        depth = 0
        for i in range(s, len(t)):
            if t[i] == "{": depth += 1
            elif t[i] == "}":
                depth -= 1
                if depth == 0:
                    try: return loads(t[s:i+1])
                    except Exception: break
        s = t.find("{", s+1)
    return None


def main():
    print("═" * 66)
    print("  👺👺👺 GOBLIN CHIDDUSH SWARM — agentics corpus")
    print("  authority=false · chiddush=hypothesis-generator, NOT fact")
    print("═" * 66, flush=True)
    out = []
    for name, model, lens, brief in GOBLINS:
        user = f"{CORPUS}\n\nYour lens: {lens} — {brief}.\n\n{SCHEMA}"
        t0 = time.time()
        try:
            raw = ollama(model, SYS, user)
        except Exception as e:
            raw = f"__ERROR__ {e}"
        dt = time.time() - t0
        c = extract(raw) or {"chiddush": "(unparsed)", "raw": raw[:400]}
        c.update({"_goblin": name, "_model": model, "_lens": lens, "_s": round(dt, 1)})
        out.append(c)
        print(f"\n👺 {name}  ·  {model}  ·  {lens}   [{dt:.1f}s]")
        print(f"   🌿 SEED     {str(c.get('seed_root'))[:80]}")
        print(f"   🔦 CHIDDUSH {str(c.get('chiddush'))[:200]}")
        print(f"   🟣 HYPOTH   {str(c.get('hypothesis'))[:170]}")
        print(f"   🔬 DISCRIM  {str(c.get('discriminator'))[:170]}")
        print(f"   ⚗ WULMATH  {str(c.get('wulmath'))[:120]}   ⚫ authority=0", flush=True)
    (ROOT / "GOBLIN_SWARM_CHIDDUSH_V0.json").write_text(
        json.dumps({"schema": "GOBLIN_SWARM_CHIDDUSH_V0", "authority": False,
                    "canon": False, "layer": "TEMPLE", "chiddush": out},
                   indent=2, ensure_ascii=False))
    print("\n═" * 1 + "═" * 65)
    print("  swarm complete →", len(out), "chiddush candidates · authority=0 · not canon")


if __name__ == "__main__":
    main()
