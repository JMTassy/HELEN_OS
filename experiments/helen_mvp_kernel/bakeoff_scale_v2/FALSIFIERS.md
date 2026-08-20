<!-- authority=false · canon=false · ledger_effect=none · spec only -->

# SCALE_V2 — FALSIFICATION PROTOCOL (frozen before code)

Falsification runs **after** canonical propositions + provenance roots exist, and gates `N_F`.

## Per canonical proposition
1. **State the strongest concrete falsifier** — the specific observation that, if present in the frozen scope, would refute the proposition. Vague/unfalsifiable → `INCONCLUSIVE` (not SURVIVED).
2. **Actively search for counter‑evidence** within the frozen scope only (no scope expansion mid‑run).
3. **Return one verdict:** `SURVIVED | REFUTED | INCONCLUSIVE`.
   - `REFUTED` — counter‑evidence found in scope.
   - `INCONCLUSIVE` — no decisive evidence either way, or falsifier not concrete.
   - `SURVIVED` — not refuted under this falsifier and this scope.

## What SURVIVED does and does not mean
```
HAL_SURVIVED  ==  "not refuted under this falsifier and scope"
HAL_SURVIVED  !=  TRUE
HAL_SURVIVED  !=  ADMITTED           (admission is Γ_A, which does not run here → N_L = 0)
HAL_SURVIVED  !=  INDEPENDENTLY_CORROBORATED   (that is N_E's job, a separate stage)
```
`FailureToFalsify(p) ⇏ Truth(p)`. A proposition can SURVIVE with `N_E = 1` (single root) — surviving falsification and having independent provenance are **different** properties, reported separately.

## N_F counting
`N_F = |{ (proposition, independent_root) : HAL = SURVIVED }|`. A proposition surviving on 1 independent root contributes 1; the same proposition is **not** multiplied by paraphrase count or agent count (those were already collapsed in Stages 1–2).

## Reporting buckets (always emitted, never hidden)
- `REFUTED_CLAIMS` — with the refuting witness.
- `INCONCLUSIVE_CLAIMS` — with what evidence is missing.
- `UNKNOWN_ANCESTRY` — propositions whose provenance independence is `UNKNOWN` (held out of `N_E`).
- `FANOUT_COLLAPSES` — raw→canonical and multi‑agent→single‑root collapses (the anti‑fan‑out audit trail).

Silence is not a pass: a proposition not evaluated is `INCONCLUSIVE`/`NOT_EVALUABLE`, never `SURVIVED`. `NOT_EVALUABLE ≠ 0`.
