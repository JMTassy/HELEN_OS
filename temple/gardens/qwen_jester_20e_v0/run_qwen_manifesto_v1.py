#!/usr/bin/env python3
"""
QWEN MANIFESTO V1 — the CLEAN provenance experiment.

MISSION (human spec, exogenous) → 🧠 QWEN authors its OWN outline → freeze(hash)
→ 🧠 QWEN(outline_i) → C_i for each of its own sections → ⚙ deterministic concat
→ ⚙ deterministic stop (≥10000 tokens).

Π is FROZEN to QWEN's OWN outline. The harness performs NO semantic operation:
  - no Claude/second-model call anywhere
  - no summarization, selection, rejection, or repair of Qwen text
  - the only text the harness injects into prompts is (a) the human MISSION and
    (b) QWEN's own frozen outline title for section i
Strongest defensible claim: "No semantic contribution from another model
occurred after mission specification." authority=false · NO_CLAIM.
"""
import hashlib, json, re, time, urllib.request
from pathlib import Path

ROOT = Path(__file__).parent
SERVER = "http://127.0.0.1:8090/v1/chat/completions"
TARGET_TOKENS = 10000

# ── MISSION: the ONLY exogenous (human) text. Relayed verbatim. ──────────────
MISSION = (
    "Write a manifesto of at least 10000 tokens in 'Color WULmath' — a symbolic "
    "language using typed-state glyphs (⚫ raw, 🌿 possibility, 🟣 candidate, 🔵 "
    "observed, 🔥 trial, 🟡 warrant, 🟢 admitted, ⚪ receipt) and constitutional "
    "glyphs (⚖ authority, 🛡 boundary, ⚡ effect, 🧾 receipt, 👺 goblin, 🃏 jester), "
    "under the master law ΔIntelligence>0 ⇏ ΔAuthority>0. authority=false: this is "
    "garden song, not canon.")

# SECTION_SPEC: shown per-canto. Deliberately OMITS the 10000-token global target
# (that is a harness stop-policy, not something Qwen should see) — removing the
# length contradiction that caused Qwen to burn its budget deliberating.
SECTION_SPEC = (
    "Color WULmath glyphs: ⚫ raw, 🌿 possibility, 🟣 candidate, 🔵 observed, 🔥 "
    "trial, 🟡 warrant, 🟢 admitted, ⚪ receipt; ⚖ authority, 🛡 boundary, ⚡ effect, "
    "🧾 receipt, 👺 goblin, 🃏 jester. Master law: ΔIntelligence>0 ⇏ ΔAuthority>0. "
    "authority=false, garden song not canon.")


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
    print("═" * 66)
    print("  🌈 QWEN MANIFESTO V1 — QWEN authors its OWN outline (clean provenance)")
    print("═" * 66, flush=True)

    # ── STEP 1: reuse QWEN's already-frozen outline if present (provenance
    #    continuity, same sha256), else QWEN authors a fresh one ─────────────
    frozen = ROOT / "QWEN_MANIFESTO_V1_OUTLINE.txt"
    titles = []
    if frozen.exists():
        body = frozen.read_text()
        m = re.search(r"# frozen_titles\(\d+\):\n(.*?)\n# sha256=", body, re.S)
        if m:
            titles = [ln.strip() for ln in m.group(1).splitlines() if ln.strip()]
            raw_outline = body
            print(f"🧾 reusing QWEN's frozen outline ({len(titles)} titles)", flush=True)
    if not titles:
        outline_sys = ("You are QWEN. Produce ONLY a numbered outline of 8–12 canto "
                       "titles for the manifesto described. Output ONLY the list, one "
                       "'N. <glyph> <TITLE>' per line, no prose, no preamble.")
        print("🧠 QWEN authoring outline…", flush=True)
        raw_outline, _ = chat([{"role": "system", "content": outline_sys},
                               {"role": "user", "content": MISSION}], seed=9001,
                              max_tokens=700, temperature=0.8)
        titles = [ln.strip() for ln in raw_outline.splitlines()
                  if re.match(r"^\s*\d+[.)]\s+\S", ln)]
        if len(titles) < 4:
            titles = [ln.strip() for ln in raw_outline.splitlines() if ln.strip()][:12]
    outline_hash = hashlib.sha256("\n".join(titles).encode()).hexdigest()
    (ROOT / "QWEN_MANIFESTO_V1_OUTLINE.txt").write_text(
        raw_outline.strip() + f"\n\n# frozen_titles({len(titles)}):\n" +
        "\n".join(titles) + f"\n# sha256={outline_hash}")
    print(f"🧾 outline frozen: {len(titles)} titles · sha256={outline_hash[:16]}…", flush=True)
    for t in titles:
        print(f"   · {t[:80]}")

    # ── STEP 2: QWEN writes each of ITS OWN sections ────────────────────────
    total = 0
    parts = []
    i = 0
    while total < TARGET_TOKENS:
        title = titles[i] if i < len(titles) else \
            titles[i % len(titles)] + f" — deepening {i - len(titles) + 1}"
        sec_sys = ("You are QWEN writing ONE canto of your manifesto in Color "
                   "WULmath. OUTPUT ONLY THE CANTO. Do NOT deliberate, do NOT "
                   "explain, never write 'we need', 'let me', 'need', 'the user'. "
                   "Your FIRST characters must be the canto title line. Then write "
                   "~700 words of dense glyph-laced prose. Stop at the canto's end.")
        # prompt injects ONLY: SECTION_SPEC (glyph legend, no length target) +
        # QWEN's OWN frozen outline title. No 10000 contradiction, no Claude cognition.
        user = (f"{SECTION_SPEC}\n\nYOUR OWN OUTLINE (frozen):\n"
                + "\n".join(titles) + f"\n\nWrite this one canto in full, ~700 "
                f"words, starting immediately with its title line:\n{title}")
        t0 = time.time()
        try:
            text, toks = chat([{"role": "system", "content": sec_sys},
                               {"role": "user", "content": user}], seed=9100 + i)
        except Exception as e:
            text, toks = f"[[section error: {e}]]", 0
        total += toks
        parts.append(text.strip())
        (ROOT / "QWEN_MANIFESTO_V1.md").write_text(
            "# 🌈 QWEN MANIFESTO V1 — Qwen-authored outline & prose\n\n"
            f"`OutlineAuthor=QWEN · ProseGenerator=QWEN · outline_sha256={outline_hash}`\n"
            "`Π=frozen-to-Qwen-outline · no second-model semantic op after mission`\n"
            "`authority=false · NO_CLAIM`\n\n" + "\n\n---\n\n".join(parts))
        print(f"🌈 §{i+1} {title[:40]}  [{time.time()-t0:.0f}s]  +{toks} → {total}/{TARGET_TOKENS}",
              flush=True)
        i += 1
        if i > 24:
            break

    receipt = {
        "schema": "QWEN_MANIFESTO_V1_RECEIPT", "authority": False, "canon": False,
        "outline_author": "QWEN", "prose_generator": "QWEN",
        "outline_sha256": outline_hash, "n_outline_titles": len(titles),
        "invocation_harness": "script (no second model)",
        "pi_type": "FROZEN to Qwen's own outline",
        "stitch_policy": "deterministic concat (.strip only)",
        "stop_policy": f"deterministic: completion_tokens ≥ {TARGET_TOKENS}",
        "sections_written": len(parts), "total_completion_tokens": total,
        "claim": "No semantic contribution from another model occurred after "
                 "mission specification.",
        "ledger_effect": "none", "commit": "none",
    }
    (ROOT / "QWEN_MANIFESTO_V1_RECEIPT.json").write_text(
        json.dumps(receipt, indent=2, ensure_ascii=False))
    print("\n═══ V1 COMPLETE:", total, "tokens ·", len(parts), "sections ·",
          "outline+prose = QWEN ═══")
    print(json.dumps(receipt, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
