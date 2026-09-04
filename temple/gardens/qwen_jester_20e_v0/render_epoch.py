#!/usr/bin/env python3
"""Color WULmath renderer for a persisted Qwen JESTER epoch. VERBATIM fields —
no rewriting. Glyph frame only; Qwen content shown exactly as emitted."""
import json, re, sys
from pathlib import Path

EP = Path(__file__).parent / "epochs" / f"epoch_{int(sys.argv[1]):02d}.json"
r = json.load(open(EP))
raw = r["raw"]

# WULmath field → glyph map (projection only; never alters content)
GL = [
    ("SEARCH_INTENT",         "🌿 SEARCH_INTENT"),
    ("MUTATION",              "🧬 MUTATION"),
    ("COUNTERFEIT_WORLD",     "🔥 COUNTERFEIT_WORLD"),
    ("DISCRIMINATOR",         "🔬 DISCRIMINATOR (separator x*)"),
    ("TARGET_CLAIM",          "🟣 TARGET_CLAIM"),
    ("EXPECTED_OBSERVATION",  "🌿 EXPECTED_OBSERVATION"),
    ("POTENTIAL_DISTINCTION", "🟣 POTENTIAL_DISTINCTION"),
    ("REDUNDANCY_WITH_PRIOR", "⚫ REDUNDANCY_WITH_PRIOR"),
]

def field(key):
    m = re.search(rf"^{key}:\s*(.*?)(?=\n[A-Z_]+:|\Z)", raw, re.S | re.M)
    return m.group(1).strip() if m else None

if raw.startswith("__ERROR__"):
    print(f"⚫ EPOCH {r['epoch']:02d}/20 — INFRA_FAULT (not Qwen cognition): {raw.strip()}")
    sys.exit(0)

print("━" * 60)
print(f"🃏 QWEN/JESTER — EPOCH {r['epoch']:02d}/20   [{r['wall_s']:.1f}s]  🛡 AUTHORITY_DELTA=0")
print(f"   model Qwen3.8-27B-Q3-XYZ-v2 · llama-server c4096 · 🧾 epochs/{EP.name}")
print("━" * 60)
for key, label in GL:
    v = field(key)
    if v is None:
        continue
    print(f"{label}")
    for line in v.splitlines():
        print(f"    {line}")
# truncation honesty
if not field("REDUNDANCY_WITH_PRIOR") or "AUTHORITY_DELTA" not in raw.split(
        "POTENTIAL_DISTINCTION")[-1]:
    print("⚠  (artifact truncated by Qwen reasoning-budget — shown as-is, not repaired)")
