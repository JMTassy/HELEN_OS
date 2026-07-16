"""P2 vector index tests — helen_os/knowledge/ingest.py FAISS layer.

Non-sovereign: exercises retrieval only. Skips entirely if faiss/numpy are
not installed (run with .venv-knowledge: python3.13 + faiss-cpu + numpy).

Covers the five required cases:
  1. index creation + query parity vs linear scan
  2. incremental add after ingest
  3. persistent reload from disk
  4. dimension-mismatch query -> graceful linear fallback
  5. corrupted faiss_index.bin -> graceful linear fallback
Plus: stale index (ntotal != faiss_ids) -> linear fallback.
"""
import json

import pytest

np = pytest.importorskip("numpy")
pytest.importorskip("faiss")

from helen_os.knowledge import ingest

DIM = 32


@pytest.fixture()
def corpus(tmp_path, monkeypatch):
    """Isolated knowledge dir with 200 deterministic embeddings."""
    emb_dir = tmp_path / "embeddings"
    emb_dir.mkdir()
    monkeypatch.setattr(ingest, "DIM", DIM)
    monkeypatch.setattr(ingest, "EMBEDDINGS_DIR", emb_dir)
    monkeypatch.setattr(ingest, "FAISS_INDEX_PATH", tmp_path / "faiss_index.bin")
    ingest.load_embedding.cache_clear()
    ingest.EMBEDDING_CACHE.clear()
    ingest._reset_faiss_cache()

    rng = np.random.default_rng(42)
    index = {"version": 2, "chunks": [], "total_chunks": 0,
             "files_indexed": 0, "faiss_built": False}
    _add_vectors(index, emb_dir, rng, 200)
    yield index, emb_dir, rng
    ingest.load_embedding.cache_clear()
    ingest.EMBEDDING_CACHE.clear()
    ingest._reset_faiss_cache()


def _add_vectors(index, emb_dir, rng, n):
    start = index["total_chunks"]
    for i in range(start, start + n):
        vec = rng.normal(size=DIM).tolist()
        (emb_dir / f"{i}.json").write_text(json.dumps(vec))
        index["chunks"].append({"id": i, "file": f"doc_{i}.md", "chunk_index": 0,
                                "hash": f"h{i}", "chars": 100, "preview": f"chunk {i}"})
    index["total_chunks"] += n


def _query_vec(chunk_id):
    return json.loads((ingest.EMBEDDINGS_DIR / f"{chunk_id}.json").read_text())


def test_build_and_query_parity(corpus):
    index, _, _ = corpus
    ingest.build_faiss_index(index)
    assert index["faiss_built"] is True
    assert index["faiss_count"] == 200
    assert ingest.FAISS_INDEX_PATH.exists()

    q = _query_vec(7)
    faiss_top = ingest.query_faiss(q, index, 5)
    linear_top = ingest._linear_query(q, index, 5)
    assert faiss_top[0]["chunk_id"] == 7          # exact self-match
    assert faiss_top[0]["score"] == pytest.approx(1.0, abs=1e-3)  # cosine, not L2
    overlap = {r["chunk_id"] for r in faiss_top} & {r["chunk_id"] for r in linear_top}
    assert len(overlap) >= 4                       # HNSW approx recall


def test_incremental_add(corpus):
    index, emb_dir, rng = corpus
    ingest.build_faiss_index(index)
    _add_vectors(index, emb_dir, rng, 20)
    new_ids = [c["id"] for c in index["chunks"][-20:]]
    ingest.add_to_faiss_index(index, new_ids)
    assert index["faiss_count"] == 220

    q = _query_vec(210)                            # a post-build chunk
    top = ingest.query_faiss(q, index, 5)
    assert top[0]["chunk_id"] == 210               # new chunks are searchable


def test_persistent_reload(corpus):
    index, _, _ = corpus
    ingest.build_faiss_index(index)
    ingest._reset_faiss_cache()                    # simulate fresh process
    q = _query_vec(3)
    top = ingest.query_faiss(q, index, 5)
    assert top[0]["chunk_id"] == 3
    assert ingest._FAISS_CACHE["index"] is not None  # reloaded from disk


def test_dimension_mismatch_falls_back(corpus):
    index, _, _ = corpus
    ingest.build_faiss_index(index)
    bad_q = [0.5] * 8                              # wrong dimension
    result = ingest.query_faiss(bad_q, index, 5)   # must not raise
    assert result == []                            # linear skips mismatched dims


def test_corrupted_index_falls_back(corpus):
    index, _, _ = corpus
    ingest.build_faiss_index(index)
    ingest.FAISS_INDEX_PATH.write_bytes(b"NOT A FAISS INDEX")
    ingest._reset_faiss_cache()
    q = _query_vec(11)
    top = ingest.query_faiss(q, index, 5)          # must not raise
    assert top[0]["chunk_id"] == 11                # linear fallback still correct


def test_stale_index_falls_back(corpus):
    index, _, _ = corpus
    ingest.build_faiss_index(index)
    index["faiss_ids"] = index["faiss_ids"] + [9999]   # ntotal != len(faiss_ids)
    q = _query_vec(5)
    top = ingest.query_faiss(q, index, 5)
    linear = ingest._linear_query(q, index, 5)
    assert [r["chunk_id"] for r in top] == [r["chunk_id"] for r in linear]
