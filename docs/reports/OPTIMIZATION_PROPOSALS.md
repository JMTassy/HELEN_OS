# OPTIMIZATION_PROPOSALS.md

**PHASE 3 COMPLETE** (Ranked proposals from root causes; no code changes)

**A. Hash-gate deduplication** (already partial in ingest.py)
- Effort: Low (enhance existing hash set).
- Expected speedup: 10-20% on ingest.
- Maintenance: Low.
- Governance risk: None (non-sovereign).
- Classification: SAFE_OPTIMIZATION.

**B. Incremental ingest**
- Effort: Medium (track last-ingested, delta only).
- Expected speedup: 5-10x on repeated boots/ingests.
- Maintenance: Medium (state management).
- Governance risk: Low (read-only).
- Classification: SAFE_OPTIMIZATION.

**C. Persistent embedding cache**
- Effort: Low-Medium (in-memory + disk cache with TTL).
- Expected speedup: 5-8x on query (eliminate repeated loads).
- Maintenance: Low.
- Governance risk: None.
- Classification: SAFE_OPTIMIZATION.

**D. FAISS index** (already partially added in ingest.py)
- Effort: Medium (integrate IndexHNSWFlat, build on ingest).
- Expected speedup: 100-1000x on query (sub-linear NN).
- Maintenance: Medium (index rebuilds, version compatibility).
- Governance risk: None (retrieval only).
- Classification: ARCHITECTURAL_CHANGE (highest leverage).

**E. HNSW index** (variant of D, already in patch)
- Effort: Low (within FAISS).
- Expected speedup: Same as D, tunable (efConstruction).
- Maintenance: Low.
- Governance risk: None.
- Classification: ARCHITECTURAL_CHANGE.

**F. Background compaction**
- Effort: High (threaded/periodic job, salience weighting).
- Expected speedup: Ongoing (reduce drawer count over time).
- Maintenance: High.
- Governance risk: Low (if non-mutating).
- Classification: ARCHITECTURAL_CHANGE (future).

**Ranked by leverage (evidence from benchmark/root cause)**:
1. D/E (FAISS/HNSW) — primary O(N) fix.
2. C (cache) — immediate I/O win.
3. B (incremental) — boot/ingest win.
4. A (dedup).
5. F (compaction).

All proposals respect HARD STOPS and LOCAL HELEN CONTEXT (compost for vocabulary/boundary/memory/HER consistency/garden safety). No mutation, no admission.

**LOCAL HELEN CONTEXT (compost only)**:
- DOMAIN: MEMORY_SCALING
- CLAIM: FAISS/HNSW is highest-leverage non-sovereign optimization per benchmark (13.7s → <0.1s).
- OBLIGATIONS: Evidence-first, ranked proposals, no sovereign paths.
- RECEIPTS: This file + prior reports.
- STATUS: PROPOSAL_ONLY.

Evidence precedes optimization. Memory may grow. Only the reducer may admit reality.