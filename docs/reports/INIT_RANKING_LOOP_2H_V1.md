# INIT_RANKING_LOOP_2H — V1 Receipt

NON_SOVEREIGN · authority=false · canon=false · ledger_effect=none ·
reducer_required=true · NO COMMIT · NO SHIP-claim · NO ADMISSION

Loop: 2026-07-06 18:55 → 20:0x CET (terminated early — objective resolved with
verdict; padding to deadline forbidden). Roles: HER proposed, HAL gated,
fresh-context auditor attacked (proposer ≠ validator, agent aca78eb762dbe8bde).

## Baseline → best → verdict

| | Top3Match | OrderScore | Stability | score |
|---|---|---|---|---|
| baseline (type-priority only) | 0.00 | 0.25 | 1.00 | 0.15 |
| winner (w_noise=1.0, w_len=0.1) | 1.00 | 0.80 | 1.00 | 0.96 |
| **Phase-3 verdict** | | | | **KILLED** |

Weight diff vs baseline: `w_noise 0→1.0` (kept, it01) · `w_len 0→0.1` (kept,
it09) · 12 other single-weight moves rolled back. Full log:
`scratch/loop_state_init_ranking.json`.

## Why the winner is dead (auditor findings, all verified by execution)

1. **Total circularity.** `lexical_noise_kw` fires on `signals=[` — a regex
   for the operator's own batch-rejection reason. Perfect class separation by
   that one bit; ablation: w_noise alone → Top3Match 1.0; winner minus
   w_noise → Top3Match 0.0 (below baseline). The search re-derived its label.
2. **No held-out data, and none possible today.** Gold set = entire outbox
   (31 = 31); effective positives = 5 packets resampled across 20 cases.
   Generalization untested and untestable with current marks.
3. **Stability metric is a constant.** 1.0 for any weights (even absurd ones)
   via the packet_id tie-break — 0.10 of every score is free.
4. **w_len is actively wrong.** Its 0.9267→0.96 gain comes from inverting an
   acted packet below a deferred one; the trivial order acted>deferred
   achieves OrderScore 1.0 and strictly dominates the winner.

## What was and was not learned (honest phrasing, per audit RULE)

- **Learned:** a noise-penalty heuristic *consistent with one operator batch
  rejection*. Predictive value unestablished. NOT "ranking weights validated
  against operator truth."
- **Learned (meta, the real yield):** the loop harness itself works —
  gate-0 pen precondition, frozen evaluator, hypothesis-per-move search,
  and an adversarial phase that killed a 0.96 before it became a claim.
  This is the first full proposal → operator-truth → search → refutation
  cycle HELEN has run end to end.
- **Not learned:** any generalizing ranking signal; any correct value
  ordering among positives.

## Keep/reject rule applied

REJECT the winner weights despite raw score (Phase-3 override, as designed).
Keep the harness (goldset builder, frozen evaluator, attack protocol) as the
reusable organ.

## Next iteration target (single)

**Break the circularity first:** upgrade `autoresearch_scanner.py` from
keyword-match to crossing-detection (the operator's own rejection note
demands it), rescan, collect fresh pen marks on packets the noise-regex
cannot pre-classify → true held-out set → only then re-run the weight search.
Also fix the evaluator: replace constant Stability with input-order
perturbation over ties, and add value-order (acted>deferred) to truth.

## Artifacts

- `scratchpad/init_goldset_v1.json` — 20 cases, operator marks only
- `scratch/autoresearch_init_evaluator_v1.py` — frozen metric (defect: line 32 tie-break makes Stability constant)
- `scratch/loop_state_init_ranking.json` — full iteration log
- `scratch/build_init_goldset.py` — deterministic builder

TERMINATE — REPORT WRITTEN: docs/reports/INIT_RANKING_LOOP_2H_V1.md
NO SHIP · NO ADMISSION

*a 0.96 that dies under attack is worth more than a 0.96 that ships ·
proposal ⊬ admission · 📜 ledger sleeps*
