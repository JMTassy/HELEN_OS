# QWEN3.8-9B — HELEN SUBSTRATE BASELINE (M3 Pro 18GB) — 2026-08-16/17

Artifact: ~/models/qwen38-9b/Qwen3.8-9B-Q4_K_M.gguf (5,780,090,176 B,
sha256 df13d660…44a7a = HF-published, hash-matched at pull).
Runtime: llama-server b9430 · Metal full offload (-ngl 99) · -fa on.
Probe: frozen 384-token prompt, n_predict=128, temp 0, seed 0 — identical
at every rung (no context-usage confound).

## LADDER (all rungs STABLE — no operationally-bad point reached)

| rung             | ctx    | KV     | pp tok/s | tg tok/s | RSS GB | free% |
|------------------|--------|--------|----------|----------|--------|-------|
| baseline_8k      | 8,192  | f16    | 236.8    | 17.6     | 5.95   | 28    |
| kvq4_16k         | 16,384 | q4_0   | 213.3    | 20.1     | 5.84   | 30    |
| kvq4_32k         | 32,768 | q4_0   | 209.2    | 20.2     | 5.98   | 30    |
| kvq4_64k         | 65,536 | q4_0   | 235.0    | 20.5     | 6.26   | 26    |

STABLE_CONTEXT_BOUND_OBSERVED = 65,536 (ladder ceiling; not extrapolated).
KV-quant behaved exactly as framed: a context-memory intervention —
64K costs only +0.3 GB RSS over 8K/f16. Decode ~20 tok/s throughout:
usable discriminator speed at agentic context depth.

## MTP GATE (prescribed two-check sequence)
1. Runtime: b9430 DOES list --spec-type draft-mtp            [WITNESSED]
2. Model:   GGUF header contains NO mtp/nextn tensor keys
            (strings hits are BPE vocab tokens only)          [WITNESSED]
=> MTP rung NOT RUN. The third-party 9B distill did not retain the
   teacher's MTP head. Architecture-family support ≠ artifact support.

## SUBSTRATE ROLES (per plan)
- 2B  = cheap Goblin/control (witnessed 71.6 tok/s, CHEAP_GOBLIN runs)
- 9B  = PRIMARY HELEN DISCRIMINATOR — this baseline
- 27B = retired from this seat (HOLD_UNUSABLE_PERFORMANCE stands;
        18GB unified vs ~12.9GB Metal working set — remote seat only)
- Qualification context range: 8K–64K (witnessed, this seat)
- Boundary rule unchanged: Qwen → Candidate JSON, never Qwen → Effect.

NOT TESTED: Q_task / Q_discrim / Q_provenance / STR (frozen-packet
qualification — next verb) · long-prompt prefill at depth (probe was 384
tokens; 64K *allocation* witnessed, 64K *fill* not).
NON_SOVEREIGN · authority=false · ledger_effect=none · uncommitted.
