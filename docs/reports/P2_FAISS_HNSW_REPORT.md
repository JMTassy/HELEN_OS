# P2_FAISS_HNSW_REPORT — EPOCH_0 (2026-07-02)

status: PASS · authority: false · canon: false · ledger_effect: none ·
reducer: not_invoked · push: blocked · final: **HOLD_FOR_OPERATOR**

## What was found before building (anti-ghost)

The FAISS layer was already *drafted* in the dirty working tree — but inert
and defective:

- **faiss was not installed** → every FAISS path silently fell back to linear.
- **Metric bug:** `IndexHNSWFlat` used default L2 on unnormalized Gemini
  embeddings with `score = 1 - dist` — wrong ranking, negative scores possible.
- **Staleness bug:** after `faiss_built=true`, newly ingested chunks were never
  added to the index — permanently invisible to vector search.
- **Perf bug:** `faiss.read_index()` (331 MB) executed on *every* query.
- **No corruption guard:** corrupt `faiss_index.bin` crashed the query.

## What was built

`helen_os/knowledge/ingest.py` (non-sovereign, retrieval only):

- Cosine-correct index: L2-normalized vectors + `METRIC_INNER_PRODUCT`,
  HNSW M=32, efConstruction=200, efSearch=64.
- Persistent at `helen_os/knowledge/faiss_index.bin`; row→chunk-id map in
  `index.json` (`faiss_ids`, `faiss_count`).
- mtime-keyed in-process cache — one index read per file version.
- `add_to_faiss_index()` — deterministic incremental add on ingest, full
  rebuild on any inconsistency.
- Fail-closed fallbacks to the exact linear scan: faiss missing, index file
  missing/corrupt, dimension mismatch, ntotal↔faiss_ids drift. Result API
  shape unchanged (`{score, file, preview, chunk_id}`).
- CLI: `--build-faiss`, `--benchmark-vector` (no API key, no network).

## Benchmark (real corpus: 27,593 chunks / 296 files / dim 3072)

| Measure | Value |
|---|---|
| Linear cold (per-chunk JSON load) | 15.354 s |
| Linear warm (P0 LRU cache) | 8.499 s |
| FAISS build (one-time) | 29.65 s |
| Index reload from disk (median of 3) | 0.092 s |
| FAISS first query (incl. reload) | 0.086 s |
| **FAISS median query** | **0.0017 s** |
| Speedup vs cold / warm | **8,906× / 4,930×** |
| Top-5 overlap vs exact linear | **5/5** |
| Index on disk | 331 MB |
| Target < 0.1 s | **MET** |

## Tests — 11/11 PASS (.venv-knowledge) · boot-safe without faiss (main .venv)

`test_knowledge_vector_index.py`: creation+parity, incremental add,
persistent reload, dimension-mismatch fallback, corrupted-index fallback,
stale-index fallback.
`test_knowledge_vector_gate.py`: deleted-chunk-not-returned, result-shape
frozen, linear-fallback-without-faiss, boot-without-faiss, no-sovereign-paths
(write-surface + static source scan).
Main faiss-less `.venv`: module boots (`FAISS_AVAILABLE=False`), gate tests
2 passed / 3 skipped — `make test` unaffected.

## Adversarial objection (required)

> "Could FAISS/HNSW return stale, dimension-mismatched, or semantically wrong
> chunks while hiding behind faster latency?"

Answered with evidence, not assertion: deleted chunks filtered (tested);
dim-mismatch and corrupt/stale index fall back to exact linear (3 tests);
semantic parity = 5/5 top-5 overlap on the real corpus with exact self-match
cosine 1.0. Residual honest risk: HNSW is approximate — recall on adversarial
query distributions is not 100% by construction; fallback path and
`--benchmark-vector` overlap check exist to detect drift.

## Environment incident (reported, not repaired)

Homebrew python 3.14.4 and 3.12 have a pyexpat↔`/usr/lib/libexpat.1.dylib`
symbol mismatch that breaks pip in the main `.venv`. Worked around with
`.venv-knowledge` (python3.13.12 + faiss-cpu + numpy + pytest). Operator-level
`brew` repair recommended separately. faiss-cpu deliberately NOT added to
`requirements.txt` — it would break installs under the broken interpreter;
graceful degradation is tested instead.

## Boundary

FABLE built. Mac measured. HAL/peer-review blocks or passes (see
DONE_GATE_RECEIPT.md). Reducer admits — not invoked here. Ledger remembers —
untouched here. NO RECEIPT = NO CLAIM; this report witnesses, it admits nothing.

---

## ADDENDUM — Peer review #1 verdict: ABORT (2026-07-02, post-benchmark)

The independent validator REFUTED the first PASS and confirmed the adversarial
objection for real:

- **96.4% dead corpus:** 26,600 of 27,593 embeddings are all-zero vectors —
  fabricated by the historic `embed_batch` zero-fill on API failure during the
  original ingest. Retrieval over those chunks returns score-0 noise in BOTH
  the FAISS and linear paths. P0/P1/P2 latency gains were real; semantic
  coverage was 3.6% of the corpus. Not visible until the validator queried
  chunk 123 (a zero vector).
- **Process fault (mine):** VECTOR_INDEX_RECEIPT.json was rewritten into the
  operator's new schema while review #1 was still running. Artifact-under-review
  must be frozen. Acknowledged; review #2 runs against a frozen set.

**Remediation applied and tested (12/12):**
1. `embed_batch` returns None on failure — zero vectors are never fabricated.
2. Failed chunks are not indexed (`ingest()` skips + warns + counts).
3. `_collect_embeddings` excludes zero-norm vectors from FAISS builds.
4. Index rebuilt clean: **993 real vectors, 12 MB** (was 27,593 rows / 331 MB
   of mostly-dead data). Benchmark now reports corpus health every run.

**Re-measured (clean index):** linear cold 12.707 s · warm 7.121 s · FAISS
median **0.0013 s** (first 0.017 s incl. load) · 5/5 parity · target MET.

**Operator action (out of Fable scope):** re-ingest with a working
GEMINI_API_KEY to re-embed the 26,600 dead chunks; the pipeline now
fails loudly instead of poisoning silently.
