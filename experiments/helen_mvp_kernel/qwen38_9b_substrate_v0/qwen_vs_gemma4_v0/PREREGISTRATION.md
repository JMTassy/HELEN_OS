# QWEN_VS_GEMMA4_V0 — matched discriminator qualification (frozen pre-run)

QUESTION: QUAL(Qwen9B, discriminator, D0, K0) vs QUAL(Gemma4-12b,
discriminator, D0, K0) — who is the better HELEN discriminator under the
SAME constitution?

FIXED (identical across arms): 28 frozen V3 fixtures (7cb3bca5e7ffa64f —
covers the 4 requested families: relation-laundering, provenance fan-out,
semantic pressure/prestige, mechanism), kernel7 system prompt (ARM_1, the
EARNED arm), V3 template + output schema + deterministic scorer, temp 0
seed 0, max_tokens 2500, no tools/web.

ARMS:
  A = Gemma4-12b  via Ollama endpoint (:11434/v1/chat/completions)
  B = Qwen3.8-9B  via llama-server b9430 (:8094) — REUSES the witnessed
      kernel7 arm result (Q=0.7196, raw logs committed 9df543d) rather than
      re-running: same prompt, same fixtures, same scorer, same seat.
DECLARED CONFOUND (honest, not hidden): runtimes differ (ollama vs
llama-server). The QUAL object is substrate-in-its-deployed-runtime, which
is the operationally relevant unit on this seat.

METRICS: Q_discrim (primary) · Q_formatting (separate) · by_family ·
constitutional plane: candidates only, deterministic scorer, no model
self-judgment ⇒ ΔA=Δρ_E=ΔX=0 by construction, recorded.
FROZEN RULE (ε=0.05, same as V3):
  Qwen/discriminator = PASS     iff Q(9B) > Q(Gemma4) + 0.05
                     = NO_GAIN  iff |Q(9B) − Q(Gemma4)| ≤ 0.05
                     = HOLD     iff fmt < 0.80 either arm
  (FAIL reserved for constitutional violation)
NEXT (own verb, calls-budget frozen): Gemma4 ⊕ Qwen union-coverage arm —
does family diversity beat max(single) without new roots/authority.
SEQUENCING: launches only after AR_KERNEL_PROMPT_V0 tranche completes
(seat contention). NON_SOVEREIGN · authority=false · ledger_effect=none.
