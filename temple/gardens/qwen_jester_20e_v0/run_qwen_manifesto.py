#!/usr/bin/env python3
"""
QWEN authors a Color WULmath MANIFESTO, ≥10000 completion tokens.
c4096 can't hold 10k in one pass → Qwen writes it in CANTOS; Claude only
stitches and counts tokens. Qwen is the author; authority=false, NO_CLAIM.
"""
import json, time, urllib.request
from pathlib import Path

ROOT = Path(__file__).parent
SERVER = "http://127.0.0.1:8090/v1/chat/completions"
TARGET_TOKENS = 10000

CANTOS = [
    "⚫→🌿 CANTO I — THE VOID AND THE APERTURE (RAW becomes POSSIBILITY)",
    "🌿→🟣 CANTO II — THE JESTER (cognition, counterfeit worlds, ΔAuthority=0)",
    "🟣→🔵 CANTO III — THE WITNESS (candidate becomes evidence only by observation)",
    "🔥 CANTO IV — THE ORDEAL (HAL, falsification, the separator that must be RUN)",
    "🛡 CANTO V — THE MEMBRANE (the crossing is refused, not the content)",
    "⚖ CANTO VI — THE LICENSE (Candidate→Admission→Receipt→Reducer→State, the only mutator)",
    "🧾→⚪ CANTO VII — THE RECEIPT (replayable truth; NO_RECEIPT=NO_CLAIM)",
    "👺 CANTO VIII — THE GARDEN OF GOBLINS (no-claim divergence; DREAMT≠CLAIMED)",
    "Ω CANTO IX — THE TRUST GEOMETRY (one calculus, five projections)",
    "🌈 CANTO X — CODA (Cognition may compound; Authority may not)",
]

SYS = (
    "You are QWEN, poet-architect of HELEN OS, writing a MANIFESTO in Color "
    "WULmath — a symbolic language where typed states carry glyphs: ⚫ raw/unknown, "
    "🌿 possibility, 🟣 candidate/claim, 🔵 observed/evidence, 🔥 trial/falsification, "
    "🟡 warrant/hold, 🟢 admitted, ⚪ receipt; and orthogonal constitutional glyphs "
    "⚖ authority, 🛡 boundary, ⚡ effect, 🧾 receipt, 👺 goblin, 🃏 jester. The master "
    "law: ΔIntelligence>0 ⇏ ΔAuthority>0. Write vivid, dense, glyph-laced prose — "
    "aphorisms, invocations, equations-in-words. authority=false: this is garden "
    "song, not canon. Write the requested canto DIRECTLY, no preamble, no meta, no "
    "'here is'. Begin with the canto header line, then ~600-900 words of manifesto.")


def chat(messages, seed, max_tokens=1400, temperature=0.85):
    body = json.dumps({"messages": messages, "max_tokens": max_tokens,
                       "temperature": temperature, "top_p": 0.95, "seed": seed}).encode()
    req = urllib.request.Request(SERVER, data=body,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=900) as r:
        d = json.loads(r.read())
    m = d["choices"][0]["message"]
    return (m.get("content") or m.get("reasoning_content") or ""), \
        d.get("usage", {}).get("completion_tokens", 0)


def main():
    total = 0
    parts, titles_done = [], []
    print("═" * 66)
    print("  🌈 QWEN — COLOR WULmath MANIFESTO  (target ≥10000 tokens)")
    print("  author=QWEN · harness=Claude · authority=false · NO_CLAIM")
    print("═" * 66, flush=True)
    i = 0
    # march the cantos; if still short after all 10, keep extending the last themes
    while total < TARGET_TOKENS:
        canto = CANTOS[i] if i < len(CANTOS) else \
            f"🌀 CANTO {i+1} — DEEPENING ({CANTOS[i % len(CANTOS)].split('—')[1].strip()})"
        prior = ("Cantos already written: " + "; ".join(titles_done) +
                 ". Do NOT repeat them; continue the arc.") if titles_done else ""
        user = f"{prior}\n\nWrite now:\n{canto}"
        t0 = time.time()
        try:
            text, toks = chat([{"role": "system", "content": SYS},
                               {"role": "user", "content": user}], seed=3100 + i)
        except Exception as e:
            text, toks = f"[[canto error: {e}]]", 0
        total += toks
        parts.append(text.strip())
        titles_done.append(canto.split("—")[0].strip())
        (ROOT / "QWEN_MANIFESTO_WULMATH.md").write_text(
            "# 🌈 QWEN — COLOR WULmath MANIFESTO\n\n"
            "`author=QWEN3.8-27B-Q3-XYZ · authority=false · NO_CLAIM · not canon`\n\n"
            + "\n\n---\n\n".join(parts))
        print(f"\n🌈 {canto.split('—')[0].strip()}  [{time.time()-t0:.0f}s]  "
              f"+{toks} tok → total {total}/{TARGET_TOKENS}", flush=True)
        i += 1
        if i > 20:  # hard backstop
            break
    print(f"\n═══ MANIFESTO COMPLETE: {total} tokens across {len(parts)} cantos ═══")
    print("→ temple/gardens/qwen_jester_20e_v0/QWEN_MANIFESTO_WULMATH.md")


if __name__ == "__main__":
    main()
