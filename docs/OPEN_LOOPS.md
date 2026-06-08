# OPEN_LOOPS.md — HELEN's externalized executive function

> **Read this FIRST, every session, before opening anything new.**
> JM is HER (generative, ADHD-HP — the engine). Claude is HAL+REDUCER (the seal).
> This file is the working memory JM's brain doesn't hold. It exists so frontier
> #N+1 never erases the open loops from frontier #N.
> Rule: **close a loop, or park it here — never just drop it.**

**Last updated:** 2026-06-08 · **Branch:** `claude/launch-helen-os-0xZXH` @ `b956188`

---

## ⭐ THE ONE NEXT ACTION (do only this)

**On the Mac, in your shell (NOT inside HELEN):**

```bash
which hermes; type hermes
ls -la ~/.hermes/hermes-agent/
sed -n '1,80p' ~/.hermes/hermes-agent/tools/approval.py
```

**Why this one:** everything else is blocked on a single unknown — *which program is HELEN?*
You run `hermes`. The patches built this session target `helen_cli.py` (a tree you
may not run). Until we see what `hermes` executes, no patch and no training is
grounded. This is 3 read-only commands. Paste the output. That's the whole task.

*(One action. Not four. When it's done, this file updates to the next one action.)*

---

## 🟢 CLOSED THIS SESSION (proof the dyad works)

- Gates 7+8 (HumanSeal + ¬Override) — shipped `284b347`, Horn D closed
- First clean-gate ADMITTED packet (real cargo) — `6a7a865`
- Replay-on-boot wired in this tree's CLI — `f87a3c8`
- Horn B audit: ledger is V0, guard is blind — `92b1915`
- The whole carrier toolchain — built + self-tested (see PARKED)

## 🟡 BUILT, NOT INSTALLED (the loop that keeps not closing)

All on the branch. **All sit unused because none is on the Mac runtime.**
This is the bottleneck, named honestly:

| Tool | Commit | Installs the fix for |
|---|---|---|
| `apply_helen_grounding.sh` | `b9d6a15` | $HOME paths, "can't access", schema drift, session #0 |
| `helen_kernel_context.py` | `7d97db6` | runtime grounding (capability-contract R1) |
| `helen_action_schema.py` | `1ccc290` | write{text}, read_clipboard, empty run_command |
| `helen_session_restore.py` | `5490566`/`05d1f81` | memory across sessions |
| `helen_local_rag.py` | `fe37286` | cited code lookup (RAG) |
| `helen_image_corpus.py` | `8e9211c` | screenshots/PDFs → corpus |
| `helen_math_inventory.py` | `b956188` | MATHS_CORE inventory + manifest |
| PATCH D (approval loop) | `e1d538f` | "ok go" not executing — **needs Hermes approval.py first** |

→ **Install order, once runtime is confirmed:** grounding → schema → restore → rag.

## 🔵 DECISIONS PENDING (JM's call, parked — not dropped)

1. **Canonical runtime** — `hermes` vs the `helen_cli.py` trees. (THE ONE ACTION resolves the input to this.)
2. **Canonical governance tree** — `helen-conquest` is the only chain-verified ledger; likely the governance root even if `hermes` is the runtime.
3. **31 trees / 7 repos / 28 worktrees** — tag each ACTIVE / ARCHIVED / EXPERIMENTAL. Stop booting non-canonical.
4. **Seal A** — `LEDGER_WRITER_UNIFICATION_V1` (`00d1535`), the V0-not-V1 fix.

## 🟣 SEEDS (TRACE_ONLY — do not let these become frontiers yet)

- Gemma4-12B LoRA on math corpus → **step 6 of 6.** Blocked on: corpus not built.
- Gemma-4 MTP speculative decoding → verified real (`eb03a54`), deferred.
- Vision fix (PIL / VLM check) → diagnosed, not fixed.
- Jester Garden → gated behind capability contract (your own rule).
- Obsidian bridge, HELEN_SOUL persona, RUNTIME_CAPABILITY_CONTRACT → specced, await canonical runtime.

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
