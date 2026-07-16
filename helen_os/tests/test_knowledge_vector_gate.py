"""P2 vector index — done-gate tests (operator EPOCH_0 spec, items 7-10).

  7. deleted/missing chunks must not return stale results
  8. no sovereign paths in the module's write surface
  9. retrieval API result shape unchanged (both FAISS and linear paths)
 10. linear fallback when FAISS is unavailable (boot-safe without faiss)

Test 8 and the FAISS_AVAILABLE=False half of test 10 run everywhere;
the rest skip when faiss/numpy are absent (use .venv-knowledge).
"""
import json
from pathlib import Path

import pytest

from helen_os.knowledge import ingest

RESULT_KEYS = {"score", "file", "preview", "chunk_id"}
DIM = 32


def _needs_faiss():
    pytest.importorskip("numpy")
    pytest.importorskip("faiss")


@pytest.fixture()
def corpus(tmp_path, monkeypatch):
    _needs_faiss()
    import numpy as np
    emb_dir = tmp_path / "embeddings"
    emb_dir.mkdir()
    monkeypatch.setattr(ingest, "DIM", DIM)
    monkeypatch.setattr(ingest, "EMBEDDINGS_DIR", emb_dir)
    monkeypatch.setattr(ingest, "FAISS_INDEX_PATH", tmp_path / "faiss_index.bin")
    ingest.load_embedding.cache_clear()
    ingest.EMBEDDING_CACHE.clear()
    ingest._reset_faiss_cache()
    rng = np.random.default_rng(7)
    index = {"version": 2, "chunks": [], "total_chunks": 0,
             "files_indexed": 0, "faiss_built": False}
    for i in range(50):
        (emb_dir / f"{i}.json").write_text(json.dumps(rng.normal(size=DIM).tolist()))
        index["chunks"].append({"id": i, "file": f"doc_{i}.md", "chunk_index": 0,
                                "hash": f"h{i}", "chars": 100, "preview": f"chunk {i}"})
    index["total_chunks"] = 50
    yield index, emb_dir
    ingest.load_embedding.cache_clear()
    ingest.EMBEDDING_CACHE.clear()
    ingest._reset_faiss_cache()


def _vec(emb_dir, cid):
    return json.loads((emb_dir / f"{cid}.json").read_text())


def test_deleted_chunk_not_returned(corpus):
    """A chunk removed from the index must never come back from FAISS (no stale hits)."""
    index, emb_dir = corpus
    ingest.build_faiss_index(index)
    target = _vec(emb_dir, 20)
    top = ingest.query_faiss(target, index, 5)
    assert top[0]["chunk_id"] == 20              # present before deletion

    index["chunks"] = [c for c in index["chunks"] if c["id"] != 20]  # delete chunk 20
    top_after = ingest.query_faiss(target, index, 5)
    assert all(r["chunk_id"] != 20 for r in top_after)
    assert top_after, "deletion of one chunk must not empty results"


def test_result_shape_unchanged(corpus):
    """Both retrieval paths return exactly the historical result schema."""
    index, emb_dir = corpus
    ingest.build_faiss_index(index)
    q = _vec(emb_dir, 4)
    for path_results in (ingest.query_faiss(q, index, 5),
                         ingest._linear_query(q, index, 5)):
        assert path_results
        for r in path_results:
            assert set(r.keys()) == RESULT_KEYS
            assert isinstance(r["score"], float)
            assert isinstance(r["chunk_id"], int)


def test_linear_fallback_without_faiss(corpus, monkeypatch):
    """FAISS unavailable -> query_faiss transparently serves linear results."""
    index, emb_dir = corpus
    ingest.build_faiss_index(index)               # index exists on disk...
    monkeypatch.setattr(ingest, "FAISS_AVAILABLE", False)  # ...but faiss "not installed"
    q = _vec(emb_dir, 9)
    top = ingest.query_faiss(q, index, 5)
    assert top[0]["chunk_id"] == 9
    assert [r["chunk_id"] for r in top] == \
        [r["chunk_id"] for r in ingest._linear_query(q, index, 5)]


def test_boot_without_faiss_import():
    """Module import must never require faiss/numpy (guarded import)."""
    # If this test is running, `from helen_os.knowledge import ingest` succeeded
    # regardless of faiss presence; assert the guard flag is a plain bool.
    assert isinstance(ingest.FAISS_AVAILABLE, bool)


def test_no_sovereign_paths_touched():
    """The knowledge module's write surface stays inside non-sovereign paths."""
    knowledge_dir = Path(ingest.__file__).resolve().parent
    sot_root = knowledge_dir.parents[1]
    # 1. All module write targets live under helen_os/knowledge/
    for p in (ingest.INDEX_PATH, ingest.EMBEDDINGS_DIR, ingest.FAISS_INDEX_PATH):
        assert str(Path(p).resolve()).startswith(str(knowledge_dir)), p
    # 2. Static scan: source never references sovereign write targets
    src = Path(ingest.__file__).read_text()
    for forbidden in ("town/ledger", "GOVERNANCE/", "helen_os/governance",
                      "mayor_", "oracle_town/kernel", "helen_os/schemas"):
        assert forbidden not in src, f"sovereign path reference: {forbidden}"
    # 3. The only path outside knowledge/ is the receipt target under docs/reports/
    assert (sot_root / "docs" / "reports").is_dir()


def test_zero_vectors_excluded_from_index(corpus):
    """Failed (all-zero) embeddings must never enter the FAISS index or results."""
    import numpy as np  # noqa: F401  (fixture guarantees availability)
    index, emb_dir = corpus
    # Poison 10 chunks with zero vectors (simulates historic embed-failure fill)
    zero_ids = list(range(40, 50))
    for cid in zero_ids:
        (emb_dir / f"{cid}.json").write_text(json.dumps([0.0] * DIM))
    ingest.load_embedding.cache_clear()
    ingest.EMBEDDING_CACHE.clear()
    ingest.build_faiss_index(index)
    assert index["faiss_count"] == 40                    # 50 - 10 poisoned
    assert not set(index["faiss_ids"]) & set(zero_ids)   # none admitted
    q = _vec(emb_dir, 12)
    top = ingest.query_faiss(q, index, 10)
    assert all(r["chunk_id"] not in zero_ids for r in top)
