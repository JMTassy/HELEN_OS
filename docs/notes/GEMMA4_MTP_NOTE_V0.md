# GEMMA4_MTP_NOTE_V0

**status:** verified fact (deferred action)
**authority:** false
**lifecycle:** NOTE (inference optimization — not a HELEN architecture change)
**recorded_at:** 2026-06-07T18:46:33Z
**verified_by:** operator independent check, 2026-06-07

---

## Fact (verified)

- **PR #23398** — `ggml-org/llama.cpp`, merged into `master` 2026-06-07.
- Adds **Gemma-4 MTP** (multi-token prediction / speculative decoding) with flags
  `--spec-type draft-mtp` and `--spec-draft-n-max`.
- Dense Gemma-4 benefits most. Author benchmark: **290.01s → 120.65s** (>2×) at
  `--spec-draft-n-max 4`.
- **E2B/E4B not supported yet** (dense only).
- Multi-GPU may need `--spec-draft-device`.
- Avoid quantised KV cache (`-ctk q8_0 -ctv q8_0`) — can drop draft acceptance to 0%.

## Why this is a NOTE, not a task

MTP is a **speed upgrade for the HER runtime.** It does NOT fix any current
HELEN blocker:

```
MTP does NOT fix:  wrong repo_root · read_file without path ·
                   "I cannot access filesystem" · web_search for local files
```

Those are grounding/schema failures — fixed by the four landed tools
(RAG / kernel-context / action-schema / replay), not by tokens/sec.

## When to use it

After grounding lands on the Mac runtime. Then MTP is a real win to test on the
5070. Deferred command shape (do NOT run before grounding):

```bash
llama-server \
  -m gemma-4-12b-it-Q4_K_M.gguf \
  -md gemma-4-12B-it-MTP-Q8_0.gguf \
  --spec-type draft-mtp \
  --spec-draft-n-max 2 \
  -c 32768 -fa on
# verify the draft acceptance rate is >0; avoid quantised KV cache.
```

## Priority (unchanged)

```
1. HELEN grounding / schema drift   ← current blocker
2. RAG over HELEN corpus            ← landed (helen_local_rag.py, fe37286)
3. THEN Gemma-4 QAT + MTP for speed ← this note (deferred)
4. LoRA (E2B/E4B HAL first)         ← later, on grounded+unified corpus
```

## Verdict (operator's)

> MTP: VERIFIED REAL. Use: later. Current blocker: HELEN grounding, not tokens/sec.
