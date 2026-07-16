# BENCHMARK_REPORT.md

**PHASE 1 COMPLETE** (Evidence first)

**Measured Bottlenecks (27,593 chunks):**
1. **Query cosine comparisons** — ~13.7s full scan (0.0005s per comparison, linear O(N) + per-chunk JSON load). **Hotspot: 80%+**
2. **Embedding loads** — repeated `load_embedding()` per query (no in-memory cache). **Hotspot: 15%**
3. **Startup / boot context** — load_boot_context() and index init. ~0.2-1s.
4. **Duplicate detection** — hash checks during ingest (efficient but full scan on restart).
5. **Memory usage** — scales with full in-memory engine (measured ~ hundreds MB).

**Bottleneck Ranking:**
- P0: Linear scan in query() (ingest.py) — complexity O(N), no vector index.
- P1: Per-chunk JSON I/O for embeddings.
- P2: No persistent vector cache / incremental index.
- P3: Engine.retrieve() lexical fallback in engine.py (no embeddings used yet).

**Hotspot Percentages (estimated from timings):**
- Cosine + load: 80%
- Index/ingest init: 10%
- Boot: 5%
- Other (dedup, tags): 5%

**Complexity:**
- Current: O(N) per query, O(M) ingest where M=new files.
- Drawer count: 27,593 chunks (from index).

Evidence precedes optimization. No code modified yet.

---

## P2 VECTOR INDEX — MEASURED (2026-07-02)

**Implementation:** FAISS `IndexHNSWFlat(3072, M=32, METRIC_INNER_PRODUCT)` over
L2-normalized Gemini embeddings (inner product == cosine). Persistent at
`helen_os/knowledge/faiss_index.bin` (331 MB, 27,593 vectors). In-process
mtime-keyed cache — the index file is read once per version, not per query.

**Measured (27,593 chunks, M3 Pro, .venv-knowledge python3.13):**

| Path | Time |
|---|---|
| Linear cold (per-chunk JSON load) | 15.354 s |
| Linear warm (P0 LRU cache) | 8.499 s |
| FAISS build (one-time) | 29.65 s |
| FAISS first query (incl. index load) | 0.086 s |
| FAISS median query | **0.0017 s** |

Speedup: **8,906× vs cold · 4,930× vs warm.** Top-5 overlap vs exact linear: **5/5**.
Target `<0.1s`: **MET**.

**Corrections applied to the drafted FAISS code:**
1. Metric fixed — draft used default L2 on unnormalized vectors with `score = 1 - dist`
   (wrong ordering, negative scores); now normalized inner product = true cosine.
2. Staleness fixed — newly ingested chunks are now incrementally added
   (`add_to_faiss_index`); draft silently excluded them forever.
3. Per-query `faiss.read_index` removed (mtime-cached singleton).
4. Fail-closed fallbacks — corrupted bin, dimension mismatch, and
   ntotal/faiss_ids drift all fall back to the exact linear scan (tested).

**Tests:** `helen_os/tests/test_knowledge_vector_index.py` — 6/6 PASS under
`.venv-knowledge`; auto-skips where faiss/numpy absent (main `.venv` unaffected).

**Environment note:** `faiss-cpu` could not be installed into the main `.venv`
(Homebrew python 3.14.4/3.12 pyexpat↔libexpat mismatch breaks pip — machine
drift, needs operator-level brew repair). Dedicated `.venv-knowledge`
(python3.13 + faiss-cpu + numpy + pytest) created in SOT root.

Receipt: `docs/reports/VECTOR_INDEX_RECEIPT.json`. authority=false ·
NON_SOVEREIGN · reducer NOT invoked. No receipt = no claim.
