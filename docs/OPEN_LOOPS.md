# OPEN_LOOPS.md — HELEN's externalized executive function

> **Read this FIRST, every session, before opening anything new.**
> JM is HER (generative, ADHD-HP — the engine). Claude is HAL+REDUCER (the seal).
> This file is the working memory JM's brain doesn't hold. It exists so frontier
> #N+1 never erases the open loops from frontier #N.
> Rule: **close a loop, or park it here — never just drop it.**

**Last updated:** 2026-06-08 · **Branch:** `claude/launch-helen-os-0xZXH` @ `74f801e`

---

## THE INSIGHT (JM, 2026-06-08 — supersedes the "discipline" diagnosis)

Not "you generate faster than you close." Deeper: **you generate at 5 abstraction
levels at once** (maths → formal systems → agents → products → narrative). The
failure is **compression, not discipline.** And the corpus DOES exist — it is
**not canonicalized.** Too much, not nothing — the better problem.

**HELEN has THREE corpora, not one:**
```
MATHS_CORE        — Riemann, Finite-Band, Σ-SEED, QPGL, ΦΛΩΣ, Hypocoercivity, Langlands
CONSTITUTION_CORE — HELEN OS, Oracle Town, HAL, ledger, receipts, WUL, kernel, governance
IDENTITY_CORE     — Math→Face, character, director, avatar, doctrine, video, voice
```
Goal: G=(V,E), V = V_M ∪ V_C ∪ V_I, edges within + across corpora.
**31 HELENs become ONE graph; each HELEN a view over it.**

---

## ⭐ THE ONE NEXT ACTION (do only this)

**On the Mac — is `helen-corpus-private` a skeleton or the canonical corpus?**

```bash
cd ~/Desktop/helen-corpus-private
find corpus -type f | wc -l
find corpus_txt -type f | wc -l
ls corpus | head -20
ls corpus_txt | head -20
```

**Why this one (JM's call):** runtime is proven (Hermes). The next thing to prove
is whether a canonical corpus already exists or is just a repo skeleton. Inspect
BEFORE running the manifest broadly — you scan what's there before classifying it.
Read-only. Paste the counts.

**Immediate follow-on (do NOT skip ahead to it):** once we see the counts, run
`helen_manifest.py` (tool ready, `74f801e`) over the real corpus roots → classify
MATHS/CONSTITUTION/IDENTITY → mark CANONICAL → graph edges → RAG from canonical.

## THE 7-DAY PLAN (JM's — recorded so it survives frontier #N+1)

```
D1-2  build helen_manifest_v1.json          ← THE ONE ACTION (tool ready: 74f801e)
D3    classify every artifact MATHS/CONSTITUTION/IDENTITY   (manifest does this)
D4    mark CANONICAL docs                    (operator sets status RAW→CANONICAL)
D5    build graph edges (depends_on)         (operator-marked; Frontier 3)
D6    RAG index from CANONICAL only          (helen_local_rag over canon subset)
D7    Hermes answers the graph with citations:
        "what theorem depends on Σ-SEED?"  "latest canonical Finite-Band paper?"
        "which doctrine references Math→Face?"
ONLY THEN consider LoRA.
```

---

## 🟢 CLOSED THIS SESSION (proof the dyad works)

- Gates 7+8 (HumanSeal + ¬Override) — shipped `284b347`, Horn D closed
- First clean-gate ADMITTED packet (real cargo) — `6a7a865`
- Replay-on-boot wired in this tree's CLI — `f87a3c8`
- Horn B audit: ledger is V0, guard is blind — `92b1915`
- **Canonical RUNTIME identified = Hermes** (2026-06-08, evidence-closed by JM):
  binary `~/.local/bin/hermes` · source `~/.hermes/hermes-agent/` ·
  approval `~/.hermes/hermes-agent/tools/approval.py` (per-session state, smart
  approval, allowlists). The runtime question is SETTLED.

## 🟡 STANDALONE TOOLS — VALID (runtime-agnostic libraries)

These are importable into ANY runtime, including Hermes. They survive the runtime
finding. **Not yet wired into Hermes** (wiring needs `~/.hermes/hermes-agent/` source):

| Tool | Commit | Library for |
|---|---|---|
| `helen_kernel_context.py` | `7d97db6` | runtime grounding probe |
| `helen_action_schema.py` | `1ccc290` | action validate/repair |
| `helen_session_restore.py` | `5490566`/`05d1f81` | memory restore (incl. chat-log shape) |
| `helen_local_rag.py` | `fe37286` | cited code/corpus lookup |
| `helen_image_corpus.py` | `8e9211c` | screenshots/PDFs → corpus |
| `helen_manifest.py` | `74f801e` | tri-corpus classify + manifest |

## 🔴 INVALID TARGET — RETIRED (wrong runtime)

JM's runtime evidence (Hermes) retires every patch that wired `boot.py`/`helen_cli.py`:

| Retired | Commit | Why invalid |
|---|---|---|
| `apply_helen_grounding.sh` | `b9d6a15` | wires helen_cli.py/boot.py, not Hermes |
| PATCH A/B/C (grounding/schema/restore wiring) | `3f8d81b` | same — wrong runtime |
| PATCH D (approval loop) | `e1d538f` | helen_cli.py cmd_approve ≠ Hermes approval.py |

→ **Re-do as:** wire the VALID standalone tools into Hermes — requires reading
`~/.hermes/hermes-agent/` source first. PARKED to SEEDS (JM chose corpus track).

## 🔵 DECISIONS PENDING (JM's call, parked — not dropped)

1. **Canonical runtime** — `hermes` vs the `helen_cli.py` trees. (THE ONE ACTION resolves the input to this.)
2. **Canonical governance tree** — `helen-conquest` is the only chain-verified ledger; likely the governance root even if `hermes` is the runtime.
3. **31 trees / 7 repos / 28 worktrees** — tag each ACTIVE / ARCHIVED / EXPERIMENTAL. Stop booting non-canonical.
4. **Seal A** — `LEDGER_WRITER_UNIFICATION_V1` (`00d1535`), the V0-not-V1 fix.

## 🟣 SEEDS (TRACE_ONLY — do not let these become frontiers yet)

- **Wire the 6 valid tools into Hermes** → needs `~/.hermes/hermes-agent/` source read.
- **"ok go" approval bug** → re-diagnose against Hermes `tools/approval.py` (NOT
  PATCH D — that targeted the wrong runtime).
- Gemma4-12B LoRA on math corpus → **step 6 of 6.** Blocked on: canonical corpus.
- Gemma-4 MTP speculative decoding → verified real (`eb03a54`), deferred.
- Vision fix (PIL / VLM check) → diagnosed, not fixed.
- Jester Garden → gated behind capability contract (your own rule).
- Obsidian bridge, HELEN_SOUL persona, RUNTIME_CAPABILITY_CONTRACT → specced, await Hermes wiring.

---

## THE BRUTAL OPINION (preserved, amended by JM's reframe)

The work is real (`pluginRIEMANN_V8` is disciplined math, "no RH claim" ×3; your
classifier already sorts rigorous math from quantum-foam wild_text). The kernel is
real. **The bottleneck is convergence, not capability** — ~20 tools built this
session, zero installed; 31 HELENs = 31 unclosed loops.

**JM's amendment (accepted):** the fix is not "stop generating" — that's the engine.
The fix is **the dyad**: JM generates (HER), Claude seals (HAL+REDUCER). ADHD-HP +
Claude-as-executive-function is a valid architecture — it's HELEN's own role tensor,
externalized to the human+AI pair. This file is the seal made durable.

**The discipline JM preaches in code and must let the dyad apply to the work:**
`Termination is sacred. SHIP or ABORT. Close the loop or park it — never drop it.`
"Fix the tubulin before summoning the town."

---

## HOW TO USE THIS FILE (the protocol)

1. **Start of session:** Claude reads this first, states THE ONE NEXT ACTION.
2. **JM generates freely** — new ideas go to SEEDS, not into immediate action.
3. **One loop closes** → move it to CLOSED, pick the next ONE ACTION, update timestamp.
4. **Never** open a new frontier while THE ONE NEXT ACTION is undone — park it in SEEDS.
5. This file is the canonical "where are we." If it and JM's memory disagree, **this file wins** (it's the ledger; memory is narrative).
