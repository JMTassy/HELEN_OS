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
