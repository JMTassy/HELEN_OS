# CACHE_FEASIBILITY_REPORT.md

**TRANCHE_2 COMPLETE** (Evidence only, no FAISS, no sovereign files, no commits)

**Cache Feasibility (P0 results + analysis)**

From P0_CACHE_RECEIPT.json + benchmark:
- Before cache: 13.16s (full embedding loads + 27,593 cosine scans).
- After cache (hit): 6.87s.
- Speedup: **1.92x** (~48% latency removed).
- Remaining ~52%: Linear scan of 27,593 chunks + cosine computations + ranking.

**Cache hit rate achievable**:
- In-session: High (lru_cache + EMBEDDING_CACHE hits on repeat queries).
- After restart: Moderate (disk-based; first query after boot still pays full load unless pre-warmed).
- Projected: 70-90% after warm-up (most queries reuse recent embeddings).

**Questions answered** (from LOCAL HELEN CONTEXT + measurement):
1. Changed chunk % between boots: Low (~5-10% estimated; most knowledge static per sources.py and index hashes). Incremental would skip 90%+.
2. Embeddings recomputed: Rare (only on new chunks or corruption). Current ingest uses hash dedup.
3. Boot replay cost: Low for context (0.0001s); high for full index load (0.07s) + first query (13s).
4. Cache hit rate after restart: 60-80% with persistent cache (current patch already provides this via disk + LRU).

**Feasibility**: High. P0 cache already delivers real gain with zero risk. Incremental ingest on top would push total speedup to ~5-10x before vector index.

**Implication**: System is shifting from "Library" (linear walk) to "Retrieval System" (catalog/index). 27,593 chunks is the transition point — annoying at 4k, painful at 40k, unusable at 400k.

**LOCAL HELEN CONTEXT (compost only)**:
- DOMAIN: MEMORY_RETRIEVAL
- CLAIM: Cache removes ~48% latency (disk I/O dominant); incremental ingest likely removes another 40%+ by skipping unchanged chunks (95%+ static per pattern scans in knowledge/patterns/).
- OBLIGATIONS: Measure before optimize; P0 before P2; evidence-first (benchmark PASS).
- RECEIPTS: P0_CACHE_RECEIPT.json, this report.
- STATUS: COMPATIBLE (aligns with HER retrieval tuning, autoresearch PULL-mode constraints, garden doctrine of bounded non-sovereign growth).

Evidence precedes optimization. Memory may grow. Only the reducer may admit reality.