<!-- authority=false · canon=false · ledger_effect=none · spec only -->

# SCALE_V2 — METRIC DEFINITIONS (frozen before code)

Five quantities, measured separately, **never collapsed into one another**. The whole point of V2 is that each arrow below is a *non‑implication*.

```
N_RAW  →  N_P  →  N_E  →  N_F  →  N_L
```
```
N_RAW↑  ⇏  N_P↑  ⇏  N_E↑  ⇏  N_F↑  ⇏  N_L↑
```

## N_RAW — raw claims
`N_RAW = |{ raw agent claims }|` — every proposition emitted by any goblin, before any merge. Raw claim keys are **preserved permanently** (never deleted by canonicalization).

## N_P — canonical semantic propositions
After structural normalization + semantic canonicalization: `N_P = |{ canonical propositions }|`.
> 5 paraphrases of "Tarot originated in Europe" → **1** canonical proposition.
`LexicalDistinct ⇏ SemanticDistinct`. Merging is evidence‑gated (see `CANONICALIZATION_RULES.md`); raw keys survive the merge.

## N_E — independent provenance roots
For each canonical proposition, resolve provenance to an **ancestry graph** and count *independent source roots* (not documents, not agents):
`N_E = |{ independent provenance roots supporting the canonical propositions }|`.
> 5 agents citing the same book → `N_E = 1`.  1 proposition from 3 genuinely disjoint sources → `N_E = 3`.
`SemanticDistinct ⇏ EpistemicallyIndependent` · `DifferentFiles ⇏ IndependentRoots` · `DifferentAgents ⇏ IndependentRoots`.
Independence is decided by ancestry, and **unknown ancestry stays UNKNOWN, never Independent** (see `PROVENANCE_SCHEMA.json`).

## N_F — falsification‑surviving units
Count only (proposition, root) units that survive their declared falsifier under the frozen scope:
`N_F = |{ (p,e) : HAL(p,e) = SURVIVED }|`.
`HAL_SURVIVED ⇏ TRUE` · `⇏ ADMITTED` · `⇏ INDEPENDENTLY_CORROBORATED`. SURVIVED means only "not refuted under this falsifier and this scope."

## N_L — licensed / admitted units
`N_L = |{ units admitted by Γ_A }|`. For any bakeoff/pilot, **`N_L = 0` by design** — no admission step runs. This preserves the cognition/admission separation: `ΔCognition>0 ⇏ ΔAuthority>0`.

## The compression the instrument should reveal
A healthy run looks like a funnel, e.g. `N_RAW=19 → N_P=8 → N_E=5 → N_F=3 → N_L=0` — utterances → ideas → independent roots → surviving signals → (nothing admitted). Agent scaling measures **generation** (`N_RAW`); epistemic scaling measures **independent surviving roots** (`N_E`, `N_F`). They are different quantities — that is the chiddush.
