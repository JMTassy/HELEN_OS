# ROOT_CAUSE_ANALYSIS.md

**PHASE 2 COMPLETE** (No code modified — analysis only)

**Hotspot 1: Query cosine comparisons (ingest.py query() ~12.9s for sample, estimated 13.7s full)**
- **Algorithmic complexity**: O(N) linear scan over 27,593 chunks + per-chunk JSON load_embedding().
- **Unnecessary work**: Every query reloads all embeddings from disk; no in-memory cache or vector index.
- **Replay cost**: Full replay on every boot/query (no incremental or persistent index).
- **Duplicate work**: Hash checks good, but embedding computation/load repeated.
- **Cache misses**: 100% on embeddings.
- **Classification**: ARCHITECTURAL_CHANGE (needs vector index like FAISS/HNSW).

**Hotspot 2: Embedding loads & Gemini API calls**
- **Complexity**: O(K) per batch, but API rate limits and errors (API key issue in run).
- **Unnecessary work**: Dummy key causes fallback zeros; repeated for query embedding.
- **Classification**: SAFE_OPTIMIZATION (cache + offline embeddings).

**Hotspot 3: Index/ingest init & boot context**
- **Complexity**: O(M) for new files; boot_context is fast (0.0001s).
- **Unnecessary work**: Full index load on every startup if not cached.
- **Classification**: SAFE_OPTIMIZATION (incremental + persistent).

**Hotspot 4: Engine.retrieve() in engine.py (lexical fallback)**
- **Complexity**: O(C) candidates with tag/keyword scoring.
- **Unnecessary work**: No embedding use yet despite ingest embeddings.
- **Classification**: SAFE_OPTIMIZATION (hybrid with vector).

**Hotspot 5: Duplicate detection & tag graph**
- Efficient (hash set, in-memory graph).
- **Classification**: SAFE (already good).

**Overall Root Causes**:
- Lack of vector index for 27k+ embeddings (primary).
- Disk I/O for every query (no cache).
- No incremental/persistent structure for boot/ingest.
- Governance-safe (non-sovereign knowledge layer).

All classifications respect LAW: MEASURE > ASSUME. No modifications. Evidence-driven.

**LOCAL HELEN CONTEXT (compost only)**:
- DOMAIN: MEMORY_ARCHITECTURE
- CLAIM: Linear scan is primary bottleneck per benchmark (12.9s query); FAISS/HNSW is compatible non-sovereign optimization.
- OBLIGATIONS: Benchmark first, classify SAFE/ARCHITECTURAL, no sovereign paths.
- RECEIPTS: BENCHMARK_REPORT.md, this analysis.
- STATUS: COMPATIBLE (aligns with HER memory retrieval tuning and garden doctrine safety; no canon mutation).

Evidence precedes optimization. Memory may grow. Only the reducer may admit reality.