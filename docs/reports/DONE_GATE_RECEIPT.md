# DONE_GATE_RECEIPT — P2_FAISS_HNSW_VECTOR_INDEX (EPOCH_0)

status = PASS
authority = false · canon = false · ledger_effect = none · reducer = not_invoked · push = blocked
final = HOLD_FOR_OPERATOR
date = 2026-07-02

verifier = independent peer-review sub-agent, fresh context (K2/Rule 3: proposer ≠ validator).
Two rounds. Proposer (Claude Fable session) did not self-admit.

objection_tried = "Could FAISS/HNSW return stale, dimension-mismatched, or
semantically wrong chunks while hiding behind faster latency?"

## Review round 1 — verdict: ABORT (recorded, not hidden)

The objection was CONFIRMED in the strongest possible way:
- Validator's live self-match on chunk 123 failed (score 0.0) → root cause:
  **26,600 / 27,593 corpus embeddings (96.4%) were all-zero vectors** — a
  pre-existing poisoning from `embed_batch`'s zero-fill on embedding-API
  failure during the original ingest. Both FAISS and linear paths were
  serving a mostly-dead corpus.
- Process fault by proposer: receipt rewritten mid-review (operator schema
  migration) — artifact-under-review must be frozen. Acknowledged.

## Remediation (tested)

1. `embed_batch` returns None on failure — never fabricates zero vectors.
2. `ingest()` skips + counts failed chunks; total_chunks stays truthful.
3. `_collect_embeddings` excludes zero-norm vectors from every FAISS build.
4. Index rebuilt clean: 993 real vectors, 11.9 MB (was 27,593 rows / 331 MB).
5. `--benchmark-vector` now reports corpus health on every run.
6. New test: `test_zero_vectors_excluded_from_index`.

## Review round 2 — verdict: PASS (8/8 criteria)

- freeze-check: sha256 of receipt and ingest.py identical at review start
  (20:00:50Z) and end (20:03:09Z) — no mid-review mutation this time.
- 12/12 tests pass (.venv-knowledge); 0 failures under faiss-less main .venv
  (boot-safe, `FAISS_AVAILABLE=False`).
- receipt + benchmark JSON fields verified, including honest ABORT history.
- clean index verified independently (993 vectors; zero-chunk 123 confirmed
  all-zero AND absent from faiss_ids).
- live self-match: 0.0053 s, score 1.0 → LIVE QUERY PASS.
- sovereign firewall intact (git status re-checked by validator).
- validator's own refutation attempt (zero-vector query, wrong-dim query
  against the real index): no crash, no NaN, graceful degradation —
  refutation failed.

evidence_checked = pytest output (12/12 + skip-run), VECTOR_INDEX_RECEIPT.json,
VECTOR_INDEX_BENCHMARK.json, faiss_index.bin (11.9 MB), index.json faiss_count,
live query reproduction, git status, source inspection of ingest.py, sha256
freeze hashes.

## Measured result (clean index, 27,593-chunk corpus, 993 real embeddings)

linear cold 12.707 s · linear warm (P0) 7.121 s · FAISS median **0.0013 s**
(first query 0.017 s incl. load) · top-5 parity 5/5 · target < 0.1 s: **MET**

## Blocked-on-operator (not blocking this gate)

- Corpus repair: re-ingest with working GEMINI_API_KEY to re-embed the
  26,600 dead chunks (pipeline now fails loudly instead of poisoning).
- Homebrew python 3.14.4/3.12 pyexpat↔libexpat mismatch breaks pip in the
  main .venv — operator-level brew repair; `.venv-knowledge` (3.13) is the
  working stand-in.
- Reducer/MAYOR review of this packet for any admission. Nothing here is
  admitted; this receipt witnesses.

NO RECEIPT = NO CLAIM · NO_RECEIPT = NO_SHIP · proposer ≠ validator · HOLD 🌿
