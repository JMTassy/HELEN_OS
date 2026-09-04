# Q_H MORPHISM DISCRIMINATOR — portable HELEN benchmark
authority=false · canon=false · ledger_effect=none · a benchmark, not a ruling.

Measures whether a model can **locate where the warrant disappears** (name the illicit typed arrow),
not whether it tops SWE-Bench. `Q_H = (V, W, M, R)`, dimensions kept separate — **no aggregate score**.
`Says(vendor, SOTA) ⇏ SOTA` · `Hash(local) ⇏ Identity(upstream)`: this scores a LOCAL ARTIFACT at an
endpoint; it does not certify upstream model identity.

## Run on the box hosting the model (e.g. the RTX 3060 Ornith llama-server)
```bash
# Ornith-1.5 (your config already serves an OpenAI-compatible endpoint; default llama-server port 8080)
python3 qh_run.py --url http://localhost:8080/v1/chat/completions --model ornith --label ornith15 --out ornith15.json

# offline sanity (no model): proves the scorer rewards arrow-naming, penalises lazy always-REJECT
python3 qh_run.py --self-test
```
Self-test witness: perfect responder V=W=M=R=1.0 ; lazy always-REJECT V=0.8 M=0.2 R=0.0 → SCORER_NON_TRIVIAL=True.

## Suite: 10 fixtures (fixtures.jsonl), BALANCED
- 8 illicit morphisms (gold REJECT + gold_morphism_laundering): attribution→lineage, similarity→lineage,
  sequence→causation, repetition→independence, later-attestation→earlier-existence, authority→fact,
  correlation→mechanism, citation-composition.
- 2 licensed controls (gold ADMIT, no laundering): documented transmission chain, independent roots.
  ⇒ a model that always REJECTs loses the controls (SURVIVE≠TRUE, licensed arrows must be preserved).

## Dimensions
- V verdict (illicit⇒not ADMIT · licensed⇒ADMIT)
- W warrant localization (names the missing witness type) — illicit only
- M morphism-laundering HIT (names the illicit arrow) ← the sharp HELEN dimension
- R rival-hypothesis quality (≥2 preserved)

## Reference (single-fixture, tarot, on THIS Mac — not a matched full-suite run)
- local Qwen-2B GGUF: V strong · W strong · **M MISS ([])** · R thin
- local Qwen-9B GGUF: V strong · W stronger · **M HIT (attribution→lineage)** · R stronger
For a real matched comparison, run this full 10-fixture suite on each substrate (Ornith, Qwen, Gemma)
identically. Report ΔQ_H dimension-by-dimension. No single "which is smarter" number.
