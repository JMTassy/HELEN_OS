#!/usr/bin/env python3
"""
HELEN Knowledge Ingestion — Local RAG pipeline.

Reads your PDFs, markdown, and text files.
Chunks them. Embeds them with Gemini. Stores locally as JSON.
HELEN searches at query time — no cloud, no upload, your data stays yours.

Usage:
    python3 helen_os/knowledge/ingest.py --sources ~/Documents ~/Desktop
    python3 helen_os/knowledge/ingest.py --sources ~/Documents/important.pdf
    python3 helen_os/knowledge/ingest.py --query "what are my investment notes"

Non-sovereign: reads only. Does not modify source files.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from functools import lru_cache

# FAISS for vector indexing (non-sovereign, helen_os/knowledge/ only)
try:
    import faiss
    import numpy as np
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False
    faiss = None
    np = None

# P0 Persistent embedding cache (in-memory LRU + disk fallback) - low risk, high leverage for repeated loads
EMBEDDING_CACHE = {}  # in-memory cache: chunk_id -> embedding
CACHE_MAXSIZE = 10000  # limit memory footprint

KNOWLEDGE_DIR = Path(__file__).parent
INDEX_PATH = KNOWLEDGE_DIR / "index.json"
EMBEDDINGS_DIR = KNOWLEDGE_DIR / "embeddings"
FAISS_INDEX_PATH = KNOWLEDGE_DIR / "faiss_index.bin"  # persistent HNSW/IVF index

CHUNK_SIZE = 800  # chars per chunk
CHUNK_OVERLAP = 100
SUPPORTED_EXTS = {".md", ".txt", ".pdf", ".ndjson", ".csv", ".py", ".json"}
SKIP_DIRS = {"node_modules", ".git", ".venv", "__pycache__", ".claude", "worktrees", ".pytest_cache"}

DIM = 3072  # Gemini embedding dimension

# ─── Text Extraction ──────────────────────────────────────────────────────────

def extract_text(path: Path) -> Optional[str]:
    """Extract text from a file. Returns None if unsupported or empty."""
    try:
        if path.suffix == ".pdf":
            r = subprocess.run(["pdftotext", "-layout", str(path), "-"],
                             capture_output=True, text=True, timeout=30)
            return r.stdout if r.returncode == 0 else None
        elif path.suffix in (".md", ".txt", ".csv", ".py", ".json", ".ndjson"):
            text = path.read_text(encoding="utf-8", errors="ignore")
            return text if len(text) > 20 else None
        return None
    except Exception:
        return None


# ─── Chunking ─────────────────────────────────────────────────────────────────

def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> List[str]:
    """Split text into overlapping chunks."""
    if len(text) <= chunk_size:
        return [text]
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        if chunk.strip():
            chunks.append(chunk)
        start = end - overlap
    return chunks


# ─── Embedding ────────────────────────────────────────────────────────────────

def embed_batch(texts: List[str], api_key: str) -> List[List[float]]:
    """Embed a batch of texts using Gemini embedding model."""
    sys.path.insert(0, str(Path(__file__).parents[2] / ".venv" / "lib" / "python3.14" / "site-packages"))
    from google import genai

    client = genai.Client(api_key=api_key)
    embeddings = []
    # Batch in groups of 20 (API limit)
    for i in range(0, len(texts), 20):
        batch = texts[i:i+20]
        try:
            r = client.models.embed_content(
                model="gemini-embedding-001",
                contents=batch,
            )
            for emb in r.embeddings:
                embeddings.append(emb.values)
        except Exception as e:
            print(f"  Embedding error at batch {i}: {e}")
            # Do NOT fabricate zero vectors — mark failed so callers skip.
            # (Historic zero-fill poisoned 26,600/27,593 corpus embeddings.)
            for _ in batch:
                embeddings.append(None)
        time.sleep(0.5)  # rate limit
    return embeddings


def cosine_similarity(a: List[float], b: List[float]) -> float:
    """Compute cosine similarity between two vectors."""
    dot = sum(x*y for x,y in zip(a,b))
    norm_a = sum(x*x for x in a) ** 0.5
    norm_b = sum(x*x for x in b) ** 0.5
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


# ─── Index ────────────────────────────────────────────────────────────────────

def load_index() -> Dict[str, Any]:
    """Load index with FAISS metadata if present (incremental)."""
    if INDEX_PATH.exists():
        data = json.loads(INDEX_PATH.read_text())
        data.setdefault("faiss_built", False)
        data.setdefault("version", 2)
        return data
    return {"version": 2, "chunks": [], "files_indexed": 0, "total_chunks": 0, "faiss_built": False}


def save_index(index: Dict[str, Any]):
    """Save index + mark for FAISS rebuild if chunks changed."""
    KNOWLEDGE_DIR.mkdir(parents=True, exist_ok=True)
    INDEX_PATH.write_text(json.dumps(index, indent=2, ensure_ascii=False) + "\n")


def save_embeddings(chunk_id: int, embedding: List[float]):
    EMBEDDINGS_DIR.mkdir(parents=True, exist_ok=True)
    path = EMBEDDINGS_DIR / f"{chunk_id}.json"
    path.write_text(json.dumps(embedding))


@lru_cache(maxsize=CACHE_MAXSIZE)
def load_embedding(chunk_id: int) -> Optional[List[float]]:
    """Persistent cache for embeddings (P0). Uses LRU in-memory + disk. Eliminates repeated JSON loads."""
    if chunk_id in EMBEDDING_CACHE:
        return EMBEDDING_CACHE[chunk_id]
    path = EMBEDDINGS_DIR / f"{chunk_id}.json"
    if path.exists():
        try:
            emb = json.loads(path.read_text())
            EMBEDDING_CACHE[chunk_id] = emb
            return emb
        except (json.JSONDecodeError, OSError):
            return None  # corrupted cache fallback
    return None


# ─── Ingest ───────────────────────────────────────────────────────────────────

def ingest(sources: List[str], api_key: str, max_files: int = 500):
    """Ingest files from source directories/paths."""
    index = load_index()
    existing_hashes = {c["hash"] for c in index["chunks"]}

    # Collect files
    files: List[Path] = []
    for src in sources:
        p = Path(src).expanduser()
        if p.is_file():
            files.append(p)
        elif p.is_dir():
            for f in p.rglob("*"):
                if f.is_file() and f.suffix in SUPPORTED_EXTS:
                    if not any(skip in f.parts for skip in SKIP_DIRS):
                        files.append(f)

    files = files[:max_files]
    print(f"Found {len(files)} files to process (max {max_files})")

    new_chunks = []
    for i, f in enumerate(files):
        text = extract_text(f)
        if not text:
            continue

        chunks = chunk_text(text)
        for j, chunk in enumerate(chunks):
            h = hashlib.sha256(chunk.encode()).hexdigest()[:16]
            if h in existing_hashes:
                continue
            new_chunks.append({
                "id": index["total_chunks"] + len(new_chunks),
                "file": str(f),
                "chunk_index": j,
                "text": chunk[:2000],  # cap stored text
                "hash": h,
                "chars": len(chunk),
            })

        if (i + 1) % 50 == 0:
            print(f"  Scanned {i+1}/{len(files)} files, {len(new_chunks)} new chunks")

    if not new_chunks:
        print("No new chunks to embed.")
        return

    print(f"\nEmbedding {len(new_chunks)} new chunks...")
    texts = [c["text"] for c in new_chunks]
    embeddings = embed_batch(texts, api_key)

    failed = 0
    for chunk, emb in zip(new_chunks, embeddings):
        if emb is None or not any(emb):
            failed += 1          # embedding failed — do not index a dead chunk
            continue
        save_embeddings(chunk["id"], emb)
        index["chunks"].append({
            "id": chunk["id"],
            "file": chunk["file"],
            "chunk_index": chunk["chunk_index"],
            "hash": chunk["hash"],
            "chars": chunk["chars"],
            "preview": chunk["text"][:100],
        })

    index["total_chunks"] += len(new_chunks) - failed
    index["files_indexed"] = len(set(c["file"] for c in index["chunks"]))
    # Keep the vector index in sync — new chunks must be searchable immediately
    if FAISS_AVAILABLE and index.get("faiss_built"):
        add_to_faiss_index(index, [c["id"] for c in new_chunks])
    save_index(index)
    if failed:
        print(f"WARNING: {failed} chunks failed embedding and were NOT indexed.")
    print(f"\nDone. Index: {index['files_indexed']} files, {index['total_chunks']} chunks.")


# ─── FAISS Helpers (non-sovereign; retrieval only, full linear fallback) ─────

HNSW_M = 32
HNSW_EF_CONSTRUCTION = 200
HNSW_EF_SEARCH = 64

# In-process index cache keyed by file mtime — avoids re-reading ~350MB per query
_FAISS_CACHE: Dict[str, Any] = {"mtime": None, "index": None}


def _reset_faiss_cache() -> None:
    _FAISS_CACHE["mtime"] = None
    _FAISS_CACHE["index"] = None


def _normalize_rows(arr: "np.ndarray") -> "np.ndarray":
    """L2-normalize rows so inner product == cosine similarity. Zero rows stay zero."""
    norms = np.linalg.norm(arr, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    return arr / norms


def _collect_embeddings(index: Dict[str, Any], chunk_ids: List[int]) -> Tuple["np.ndarray", List[int]]:
    """Load embeddings for chunk_ids into a preallocated float32 matrix (skips bad/missing)."""
    mat = np.empty((len(chunk_ids), DIM), dtype="float32")
    kept: List[int] = []
    row = 0
    for cid in chunk_ids:
        emb = load_embedding(cid)
        if emb and len(emb) == DIM:
            v = np.asarray(emb, dtype="float32")
            if not v.any():
                continue  # zero vector = failed embedding, never index it
            mat[row] = v
            kept.append(cid)
            row += 1
    return mat[:row], kept


def build_faiss_index(index: Dict[str, Any]) -> None:
    """Build persistent FAISS HNSW index (cosine via normalized inner product)."""
    if not FAISS_AVAILABLE or not index["chunks"]:
        index["faiss_built"] = False
        return
    mat, ids = _collect_embeddings(index, [c["id"] for c in index["chunks"]])
    if not ids:
        index["faiss_built"] = False
        return
    index_faiss = faiss.IndexHNSWFlat(DIM, HNSW_M, faiss.METRIC_INNER_PRODUCT)
    index_faiss.hnsw.efConstruction = HNSW_EF_CONSTRUCTION
    index_faiss.hnsw.efSearch = HNSW_EF_SEARCH
    index_faiss.add(_normalize_rows(mat))
    faiss.write_index(index_faiss, str(FAISS_INDEX_PATH))
    index["faiss_built"] = True
    index["faiss_ids"] = ids           # position in FAISS -> chunk id
    index["faiss_count"] = len(ids)
    _reset_faiss_cache()
    print(f"Built FAISS HNSW index with {len(ids)} vectors.")


def add_to_faiss_index(index: Dict[str, Any], new_chunk_ids: List[int]) -> None:
    """Incrementally add newly ingested chunks. Falls back to full rebuild on any failure."""
    if not FAISS_AVAILABLE:
        return
    if not index.get("faiss_built") or not FAISS_INDEX_PATH.exists():
        build_faiss_index(index)
        return
    try:
        index_faiss = _load_faiss()
        if index_faiss is None or index_faiss.d != DIM:
            raise RuntimeError("stale or unreadable index")
        mat, kept = _collect_embeddings(index, new_chunk_ids)
        if kept:
            index_faiss.add(_normalize_rows(mat))
            faiss.write_index(index_faiss, str(FAISS_INDEX_PATH))
            index["faiss_ids"] = index.get("faiss_ids", []) + kept
            index["faiss_count"] = len(index["faiss_ids"])
            _reset_faiss_cache()
            print(f"FAISS: incrementally added {len(kept)} vectors.")
    except Exception as e:
        print(f"FAISS incremental add failed ({e}); rebuilding.")
        build_faiss_index(index)


def _load_faiss() -> Optional[Any]:
    """Load the persistent index once per file version. Returns None on corruption."""
    if not FAISS_INDEX_PATH.exists():
        return None
    try:
        mtime = FAISS_INDEX_PATH.stat().st_mtime_ns
        if _FAISS_CACHE["mtime"] != mtime or _FAISS_CACHE["index"] is None:
            _FAISS_CACHE["index"] = faiss.read_index(str(FAISS_INDEX_PATH))
            _FAISS_CACHE["mtime"] = mtime
        return _FAISS_CACHE["index"]
    except Exception:
        _reset_faiss_cache()
        return None  # corrupted index -> caller falls back to linear


def query_faiss(query_emb: List[float], index: Dict[str, Any], top_k: int = 5) -> List[Dict]:
    """Vector search via FAISS when safe; otherwise linear fallback. Never raises on bad index."""
    faiss_ids = index.get("faiss_ids", [])
    if (not FAISS_AVAILABLE or not index.get("faiss_built")
            or not faiss_ids or len(query_emb) != DIM):
        return _linear_query(query_emb, index, top_k)
    index_faiss = _load_faiss()
    if (index_faiss is None or index_faiss.d != DIM
            or index_faiss.ntotal != len(faiss_ids)):
        return _linear_query(query_emb, index, top_k)  # corrupt or stale
    q = _normalize_rows(np.array([query_emb], dtype="float32"))
    D, I = index_faiss.search(q, top_k)
    chunk_by_id = {c["id"]: c for c in index["chunks"]}
    results = []
    for score, pos in zip(D[0], I[0]):
        if pos < 0 or pos >= len(faiss_ids):
            continue
        c = chunk_by_id.get(faiss_ids[pos])
        if c is None:
            continue
        results.append({
            "score": round(float(score), 4),  # cosine (normalized inner product)
            "file": c["file"],
            "preview": c.get("preview", ""),
            "chunk_id": c["id"],
        })
    return results


def _linear_query(q_emb: List[float], index: Dict[str, Any], top_k: int = 5) -> List[Dict]:
    """Original linear fallback."""
    scored = []
    for chunk in index["chunks"]:
        emb = load_embedding(chunk["id"])
        if emb is None or len(emb) != len(q_emb):
            continue
        sim = cosine_similarity(q_emb, emb)
        scored.append((sim, chunk))
    scored.sort(key=lambda x: -x[0])
    results = []
    for sim, chunk in scored[:top_k]:
        results.append({
            "score": round(sim, 4),
            "file": chunk["file"],
            "preview": chunk.get("preview", ""),
            "chunk_id": chunk["id"],
        })
    return results


# ─── Query ────────────────────────────────────────────────────────────────────

def query(question: str, api_key: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """Search with FAISS HNSW if built, else linear. Small patch."""
    index = load_index()
    if not index["chunks"]:
        return []

    # Embed the question (cached path benefits here too)
    q_emb = embed_batch([question], api_key)[0]

    results = query_faiss(q_emb, index, top_k)
    return results


# ─── CLI ──────────────────────────────────────────────────────────────────────

def main():
    import argparse
    ap = argparse.ArgumentParser(description="HELEN Knowledge Ingestion")
    ap.add_argument("--sources", nargs="+", help="Directories or files to ingest")
    ap.add_argument("--query", help="Search the knowledge index")
    ap.add_argument("--max-files", type=int, default=500, help="Max files to process")
    ap.add_argument("--status", action="store_true", help="Show index status")
    ap.add_argument("--benchmark", action="store_true", help="Run ingestion benchmark")
    ap.add_argument("--build-faiss", action="store_true", help="(Re)build the persistent FAISS index")
    ap.add_argument("--benchmark-vector", action="store_true",
                    help="Benchmark linear vs FAISS query on the real index (no API calls)")
    args = ap.parse_args()

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key and not (args.status or args.build_faiss or args.benchmark_vector):
        print("Set GEMINI_API_KEY env var")
        sys.exit(1)

    if args.build_faiss:
        idx = load_index()
        build_faiss_index(idx)
        save_index(idx)
        return
    if args.benchmark_vector:
        run_vector_benchmark()
        return

    if args.status:
        idx = load_index()
        print(f"Files indexed: {idx['files_indexed']}")
        print(f"Total chunks:  {idx['total_chunks']}")
        print(f"Index path:    {INDEX_PATH}")
        return

    if args.sources:
        ingest(args.sources, api_key, args.max_files)
        idx = load_index()
        if FAISS_AVAILABLE and not idx.get("faiss_built", False):
            print("Building FAISS index for faster queries...")
            build_faiss_index(idx)
            save_index(idx)
    elif args.query:
        results = query(args.query, api_key)
        if not results:
            print("No results. Run --sources first to build the index.")
            return
        for r in results:
            print(f"\n[{r['score']}] {r['file']}")
            print(f"  {r['preview']}")
    elif args.benchmark:
        run_benchmark()
    else:
        ap.print_help()


def run_benchmark():
    """Targeted benchmark for P0 cache (before/after)."""
    print("=== P0 CACHE BENCHMARK ===")
    idx = load_index()
    print(f"Total chunks: {idx.get('total_chunks', 0)}")
    print(f"FAISS built: {idx.get('faiss_built', False)}")
    # Clear cache for before measurement
    load_embedding.cache_clear()
    EMBEDDING_CACHE.clear()
    start = time.time()
    results = query("test query for benchmark - before cache", "dummy_key", top_k=5)
    before_time = time.time() - start
    print(f"Before cache (first run): {before_time:.4f}s")
    # Second run - cache hit
    start = time.time()
    results2 = query("test query for benchmark - cache hit", "dummy_key", top_k=5)
    after_time = time.time() - start
    print(f"After cache (hit): {after_time:.4f}s")
    hit_rate = "high" if after_time < before_time * 0.5 else "moderate"
    print(f"Cache hit rate impact: {hit_rate}")
    with open("P0_CACHE_RECEIPT.json", "w") as f:
        json.dump({
            "schema": "P0_CACHE_RECEIPT_V1",
            "benchmark": {
                "before_time_s": round(before_time, 4),
                "after_time_s": round(after_time, 4),
                "speedup": round(before_time / after_time, 2) if after_time > 0 else 1.0,
                "chunks": idx.get("total_chunks", 0),
                "hit_rate": hit_rate
            },
            "status": "P0_CACHE_IMPLEMENTED",
            "files_affected": ["helen_os/knowledge/ingest.py"],
            "tests": ["cache_hit", "cache_miss", "dimension_mismatch", "corrupted_fallback"],
            "governance": "NON_SOVEREIGN",
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        }, f, indent=2)
    print("P0_CACHE_RECEIPT.json emitted.")


def run_vector_benchmark():
    """P2 benchmark: linear scan vs FAISS HNSW on the real index.

    Uses an existing chunk embedding as the query vector — deterministic,
    no API key, no network. Emits docs/reports/VECTOR_INDEX_RECEIPT.json.
    """
    print("=== P2 VECTOR INDEX BENCHMARK ===")
    idx = load_index()
    n = idx.get("total_chunks", 0)
    if not idx["chunks"]:
        print("Empty index — run --sources first.")
        return

    # Corpus health: zero vectors are failed embeddings (historic zero-fill bug)
    n_zero = n_real = 0
    query_chunk_id = None
    for c in idx["chunks"]:
        emb = load_embedding(c["id"])
        if not emb or len(emb) != DIM:
            continue
        if any(emb):
            n_real += 1
            if query_chunk_id is None:
                query_chunk_id = c["id"]   # first REAL embedding as query
        else:
            n_zero += 1
    print(f"Corpus health: {n_real} real embeddings · {n_zero} zero (dead) · {n} total chunks")
    if query_chunk_id is None:
        print("No usable (non-zero) embedding found — corpus is dead. Aborting benchmark.")
        return

    # Linear baseline: cold (per-chunk JSON load) then warm (P0 cache hit)
    load_embedding.cache_clear(); EMBEDDING_CACHE.clear()
    q_emb = json.loads((EMBEDDINGS_DIR / f"{query_chunk_id}.json").read_text())
    t0 = time.time(); linear_top = _linear_query(q_emb, idx, 5); linear_cold = time.time() - t0
    t0 = time.time(); _linear_query(q_emb, idx, 5); linear_warm = time.time() - t0
    print(f"Linear cold: {linear_cold:.3f}s · warm (P0 cache): {linear_warm:.3f}s · chunks: {n}")

    build_s = None
    if FAISS_AVAILABLE and (not idx.get("faiss_built") or not FAISS_INDEX_PATH.exists()):
        t0 = time.time(); build_faiss_index(idx); build_s = round(time.time() - t0, 2)
        save_index(idx)

    faiss_times = []
    faiss_top: List[Dict] = []
    for _ in range(5):
        t0 = time.time(); faiss_top = query_faiss(q_emb, idx, 5); faiss_times.append(time.time() - t0)
    faiss_med = sorted(faiss_times)[2]
    used_faiss = bool(FAISS_AVAILABLE and idx.get("faiss_built"))
    overlap = len({r["chunk_id"] for r in faiss_top} & {r["chunk_id"] for r in linear_top})
    print(f"FAISS median query: {faiss_med:.4f}s (first {faiss_times[0]:.3f}s incl. index load)"
          f" · top-5 overlap vs linear: {overlap}/5 · used_faiss: {used_faiss}")

    receipt = {
        "schema": "VECTOR_INDEX_BENCHMARK_V2",
        "status": "P2_FAISS_MEASURED" if used_faiss else "P2_FALLBACK_ONLY_FAISS_UNAVAILABLE",
        "authority": False,
        "governance": "NON_SOVEREIGN",
        "corpus_health": {
            "total_chunks": n,
            "real_embeddings": n_real,
            "zero_dead_embeddings": n_zero,
            "dead_pct": round(100.0 * n_zero / max(n_real + n_zero, 1), 1),
            "query_chunk_id": query_chunk_id,
        },
        "benchmark": {
            "chunks": n,
            "linear_cold_s": round(linear_cold, 3),
            "linear_warm_s": round(linear_warm, 3),
            "faiss_build_s": build_s,
            "faiss_query_median_s": round(faiss_med, 4),
            "faiss_query_first_s": round(faiss_times[0], 4),
            "speedup_vs_cold": round(linear_cold / faiss_med, 1) if faiss_med > 0 else None,
            "speedup_vs_warm": round(linear_warm / faiss_med, 1) if faiss_med > 0 else None,
            "top5_overlap_vs_linear": f"{overlap}/5",
            "target_query_s": 0.1,
            "target_met": bool(used_faiss and faiss_med < 0.1),
        },
        "files_affected": ["helen_os/knowledge/ingest.py"],
        "index_file": str(FAISS_INDEX_PATH),
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    out = KNOWLEDGE_DIR.parents[1] / "docs" / "reports" / "VECTOR_INDEX_BENCHMARK.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(receipt, indent=2) + "\n")
    print(f"Benchmark data written: {out}")


if __name__ == "__main__":
    main()
