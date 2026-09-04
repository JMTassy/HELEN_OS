<!-- authority=false · canon=false · ledger_effect=none · spec only -->

# SCALE_V2 — CANONICALIZATION RULES (frozen before code)

Two ordered stages. **Structural first, semantic second, provenance is a *separate* third stage** (see `PROVENANCE_SCHEMA.json`). Embeddings/entailment may aid the semantic stage; they may **never** decide independence.

## Stage 0 — STRUCTURAL NORMALIZATION
Parse each raw claim into `(predicate, object, scope, polarity)`. Lowercase, strip punctuation, normalize whitespace, resolve trivial synonyms of the *predicate slot* only. Output is a structural tuple, not a merge.

## Stage 1 — SEMANTIC CANONICALIZATION
Merge raw claims into canonical propositions, **evidence‑gated**:
1. **Structural identity first.** Two claims with the same `(predicate, object, scope)` and same polarity merge immediately — no model needed.
2. **Semantic merge only when strongly supported.** For structurally‑different claims, merge iff **mutual entailment** holds (each entails the other) under an entailment/NLI judge. Embedding cosine similarity is an *aid to propose* candidate merges, **never** the merge decision — similar ≠ equivalent.
3. **Preserve raw keys.** Every canonical proposition keeps `raw_claim_keys[]` back to every raw claim merged into it. **Raw claims are never deleted.** The merge is reversible/inspectable.
4. **Conservative on doubt.** If entailment is only one‑directional or uncertain → **do not merge** (keep separate). Over‑merging hides real diversity; the fail‑closed direction here is *keep distinct*.

`LexicalDistinct ⇏ SemanticDistinct` (Stage 1 collapses paraphrases) — but Stage 1 output is only `N_P`. It says nothing about independence.

## Stage 2 — PROVENANCE ROOT RESOLUTION (separate stage)
Runs *after* canonical propositions exist. Build the ancestry graph `G_E`, collapse sources joined by known ancestry, count independent roots → `N_E`. `SemanticDistinct ⇏ EpistemicallyIndependent`. Unknown ancestry → `UNKNOWN`, never Independent.

## Why the stages must stay separate
Embeddings answer *"are these propositions similar in meaning?"* — a Stage‑1 question. They **cannot** answer *"do these propositions have independent evidentiary ancestry?"* — a Stage‑2 question. Collapsing the two is exactly the V1 failure in a subtler form. Keep them separate:

```
SemanticCanonicalization  +  ProvenanceResolution   (two stages, never fused)
```

## Guardrails
- Never delete raw claims. Merges are annotations, not destruction.
- `signal_type` is a descriptive tag, not a merge criterion.
- A merge that cannot cite its basis (`STRUCTURAL_IDENTITY` or `SEMANTIC_ENTAILMENT`) is invalid.
- Independence defaults to `UNKNOWN`; establishing `INDEPENDENT` requires positive absence of known ancestry within the observed corpus.
