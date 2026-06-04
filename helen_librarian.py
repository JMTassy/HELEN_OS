"""
helen_librarian.py — HELEN OS memory substrate layer.

Constitutional rule (enforced everywhere):
    librarian.retrieve() → informs proposals
    kernel.propose()     → admits to ledger

The librarian NEVER writes to the ledger.
The librarian NEVER calls GovernanceVM.

Below the sovereign kernel. Never calls GovernanceVM.
Above the raw files. Provides structured retrieval.

MemPalace patterns adapted:
1. Transcript normalization (multi-format → clean chunks)
2. Conversation/file miners (chunks → DrawerStore)
3. Entity registry + invalidation (temporal knowledge graph)
4. Layered retrieval L0-L3 (budget-capped, scored)
"""

from __future__ import annotations

import hashlib
import json
import math
import re
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path

try:
    import urllib.request as _urllib_request
    import urllib.error as _urllib_error
    _HAS_URLLIB = True
except ImportError:
    _HAS_URLLIB = False


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def _md5(text: str) -> str:
    return hashlib.md5(text.encode("utf-8")).hexdigest()


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# Class 1: TranscriptNormalizer
# ---------------------------------------------------------------------------

class TranscriptNormalizer:
    """Normalizes multiple transcript formats into uniform turn dicts."""

    # Types that are NOT chat turns — skip them
    _SKIP_TYPES = {
        "GATE_RECEIPT", "SESSION_TURN_V1", "KERNEL_RECEIPT",
        "RECEIPT", "K_GATE", "SYSTEM_EVENT",
    }

    def normalize(self, path: Path) -> list[dict]:
        """Auto-detect format from extension + content, return normalized turns."""
        text = path.read_text(encoding="utf-8", errors="replace")
        ext = path.suffix.lower()

        if ext == ".ndjson" or self._looks_like_ndjson(text):
            lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
            return self._from_ndjson(lines)

        return self._from_plain_text(text)

    def _looks_like_ndjson(self, text: str) -> bool:
        first = text.lstrip()
        return first.startswith("{")

    def _from_ndjson(self, lines: list[str]) -> list[dict]:
        turns = []
        for line in lines:
            try:
                raw = json.loads(line)
            except json.JSONDecodeError:
                continue
            turn = self._normalize_turn(raw)
            if turn is not None:
                turns.append(turn)
        return turns

    def _from_plain_text(self, text: str) -> list[dict]:
        paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
        ts = _utcnow()
        return [{"role": "user", "content": p, "ts": ts} for p in paragraphs]

    def _normalize_turn(self, raw: dict) -> dict | None:
        # Skip known non-chat record types
        record_type = raw.get("type", "")
        if record_type in self._SKIP_TYPES:
            return None

        # ── Wisdom format: {"lesson": "...", "kind": "...", "t": "..."} ──────
        lesson = raw.get("lesson") or raw.get("value") or raw.get("content_text") or ""
        if lesson and not raw.get("role"):
            ts = raw.get("ts") or raw.get("t") or raw.get("timestamp") or _utcnow()
            kind = raw.get("kind", "lesson")
            evidence = raw.get("evidence", "")
            full = lesson
            if evidence:
                full = f"[{kind}] {lesson}\nEvidence: {evidence}"
            return {"role": "helen", "content": full, "ts": str(ts)}

        # Detect role
        role = raw.get("role") or raw.get("speaker") or ""

        # helen_chat.ndjson uses "text" not "content"
        content = raw.get("content") or raw.get("text") or ""

        # Timestamp: "ts", "t", "timestamp"
        ts = raw.get("ts") or raw.get("t") or raw.get("timestamp") or _utcnow()

        if not role or not content:
            return None

        # Normalise role aliases
        if role in ("helen", "HELEN", "assistant", "ai"):
            role = "helen"
        else:
            role = "user"

        return {"role": role, "content": str(content), "ts": str(ts)}


# ---------------------------------------------------------------------------
# Class 2: DrawerStore
# ---------------------------------------------------------------------------

_DRAWERS_DDL = """
CREATE TABLE IF NOT EXISTS drawers (
    id TEXT PRIMARY KEY,
    content TEXT NOT NULL,
    wing TEXT NOT NULL,
    room TEXT NOT NULL,
    source TEXT,
    importance REAL DEFAULT 1.0,
    embedding TEXT,
    filed_at TEXT
)
"""


class DrawerStore:
    """Verbatim content store backed by SQLite.
    Optional Ollama embeddings; graceful fallback to keyword-overlap similarity.
    """

    def __init__(self, db_path: Path, ollama_url: str = "http://localhost:11434"):
        self._db_path = db_path
        self._ollama_url = ollama_url.rstrip("/")
        self._conn = sqlite3.connect(str(db_path), check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute(_DRAWERS_DDL)
        self._conn.commit()

    # ------------------------------------------------------------------
    def add(self, content: str, wing: str, room: str,
            source: str = "", importance: float = 1.0) -> str | None:
        """Add a drawer. Returns drawer_id or None if skipped (duplicate)."""
        drawer_id = self._drawer_id(wing, room, content)

        # Duplicate check: if similarity >= 0.9 with any existing drawer → skip
        candidates = self._fetch_all_for_dedup(wing, room)
        for row in candidates:
            existing_emb = json.loads(row["embedding"]) if row["embedding"] else None
            new_emb = None  # computed lazily below

            if existing_emb is not None:
                # try to embed new content for comparison
                new_emb = self._embed(content)
                if new_emb is not None:
                    sim = self._cosine(new_emb, existing_emb)
                else:
                    sim = self._keyword_overlap(content, row["content"])
            else:
                sim = self._keyword_overlap(content, row["content"])

            if sim >= 0.9:
                return None  # skip — near-duplicate

        # Compute embedding (may be None)
        embedding = self._embed(content)
        embedding_json = json.dumps(embedding) if embedding is not None else None

        self._conn.execute(
            "INSERT OR IGNORE INTO drawers (id, content, wing, room, source, importance, embedding, filed_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (drawer_id, content, wing, room, source, importance, embedding_json, _utcnow()),
        )
        self._conn.commit()
        return drawer_id

    def search(self, query: str, wing: str = None, room: str = None,
               n: int = 5) -> list[dict]:
        """Return top-n drawers scored by similarity to query."""
        sql = "SELECT * FROM drawers WHERE 1=1"
        params: list = []
        if wing:
            sql += " AND wing = ?"
            params.append(wing)
        if room:
            sql += " AND room = ?"
            params.append(room)
        rows = self._conn.execute(sql, params).fetchall()

        query_emb = self._embed(query)
        scored = []
        for row in rows:
            row_emb = json.loads(row["embedding"]) if row["embedding"] else None
            if query_emb is not None and row_emb is not None:
                sim = self._cosine(query_emb, row_emb)
            else:
                sim = self._keyword_overlap(query, row["content"])
            scored.append({
                "id": row["id"],
                "content": row["content"],
                "wing": row["wing"],
                "room": row["room"],
                "source": row["source"],
                "similarity": sim,
                "importance": row["importance"],
            })

        scored.sort(key=lambda x: (x["similarity"], x["importance"]), reverse=True)
        return scored[:n]

    def list_by_importance(self, wing: str = None, n: int = 15) -> list[dict]:
        """Return drawers ordered by importance DESC, filed_at DESC."""
        sql = "SELECT * FROM drawers"
        params: list = []
        if wing:
            sql += " WHERE wing = ?"
            params.append(wing)
        sql += " ORDER BY importance DESC, filed_at DESC LIMIT ?"
        params.append(n)
        rows = self._conn.execute(sql, params).fetchall()
        return [dict(r) for r in rows]

    def count(self, wing: str = None) -> int:
        if wing:
            row = self._conn.execute(
                "SELECT COUNT(*) FROM drawers WHERE wing = ?", (wing,)
            ).fetchone()
        else:
            row = self._conn.execute("SELECT COUNT(*) FROM drawers").fetchone()
        return row[0]

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _fetch_all_for_dedup(self, wing: str, room: str) -> list:
        return self._conn.execute(
            "SELECT content, embedding FROM drawers WHERE wing = ? AND room = ?",
            (wing, room),
        ).fetchall()

    def _embed(self, text: str) -> list[float] | None:
        """POST to Ollama /api/embeddings. Returns vector or None on any error."""
        if not _HAS_URLLIB:
            return None
        try:
            payload = json.dumps({
                "model": "nomic-embed-text",
                "prompt": text,
            }).encode("utf-8")
            req = _urllib_request.Request(
                f"{self._ollama_url}/api/embeddings",
                data=payload,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with _urllib_request.urlopen(req, timeout=3) as resp:
                body = json.loads(resp.read())
                embedding = body.get("embedding")
                if isinstance(embedding, list) and len(embedding) > 0:
                    return [float(v) for v in embedding]
        except Exception:
            pass
        return None

    def _cosine(self, a: list[float], b: list[float]) -> float:
        """Pure Python cosine similarity."""
        if len(a) != len(b) or not a:
            return 0.0
        dot = sum(x * y for x, y in zip(a, b))
        norm_a = math.sqrt(sum(x * x for x in a))
        norm_b = math.sqrt(sum(x * x for x in b))
        if norm_a == 0.0 or norm_b == 0.0:
            return 0.0
        return dot / (norm_a * norm_b)

    def _keyword_overlap(self, query: str, content: str) -> float:
        """Jaccard similarity on tokenized words."""
        def tokens(text: str) -> set[str]:
            return set(w.lower() for w in re.split(r"[^a-zA-Z0-9]+", text) if w)

        q_tokens = tokens(query)
        c_tokens = tokens(content)
        if not q_tokens and not c_tokens:
            return 1.0
        if not q_tokens or not c_tokens:
            return 0.0
        intersection = q_tokens & c_tokens
        union = q_tokens | c_tokens
        return len(intersection) / len(union)

    def _drawer_id(self, wing: str, room: str, content: str) -> str:
        return f"drawer_{wing}_{room}_{_md5(content)[:12]}"


# ---------------------------------------------------------------------------
# Class 3: EntityRegistry
# ---------------------------------------------------------------------------

_ENTITIES_DDL = """
CREATE TABLE IF NOT EXISTS entities (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    type TEXT DEFAULT 'unknown',
    properties TEXT DEFAULT '{}',
    created_at TEXT
)
"""

_TRIPLES_DDL = """
CREATE TABLE IF NOT EXISTS triples (
    id TEXT PRIMARY KEY,
    subject TEXT NOT NULL,
    predicate TEXT NOT NULL,
    object TEXT NOT NULL,
    valid_from TEXT,
    valid_to TEXT,
    confidence REAL DEFAULT 1.0,
    source TEXT,
    extracted_at TEXT
)
"""


class EntityRegistry:
    """Temporal knowledge graph backed by SQLite."""

    def __init__(self, db_path: Path):
        self._conn = sqlite3.connect(str(db_path), check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute(_ENTITIES_DDL)
        self._conn.execute(_TRIPLES_DDL)
        self._conn.commit()

    def register(self, name: str, entity_type: str = "unknown") -> str:
        """Return entity_id, creates if new."""
        entity_id = _sha256(name.lower())[:16]
        self._conn.execute(
            "INSERT OR IGNORE INTO entities (id, name, type, properties, created_at) "
            "VALUES (?, ?, ?, '{}', ?)",
            (entity_id, name, entity_type, _utcnow()),
        )
        self._conn.commit()
        return entity_id

    def add_fact(self, subject: str, predicate: str, object: str,
                 valid_from: str = None, confidence: float = 1.0,
                 source: str = "") -> str:
        """Add a triple. Auto-registers subject and object."""
        self.register(subject)
        self.register(object)

        ts = _utcnow()
        vf = valid_from or ts
        triple_id = _sha256(subject + predicate + object + ts)[:16]

        self._conn.execute(
            "INSERT INTO triples "
            "(id, subject, predicate, object, valid_from, valid_to, confidence, source, extracted_at) "
            "VALUES (?, ?, ?, ?, ?, NULL, ?, ?, ?)",
            (triple_id, subject, predicate, object, vf, confidence, source, ts),
        )
        self._conn.commit()
        return triple_id

    def invalidate(self, subject: str, predicate: str, object: str) -> None:
        """Set valid_to = now on matching active triples."""
        now = _utcnow()
        self._conn.execute(
            "UPDATE triples SET valid_to = ? "
            "WHERE subject = ? AND predicate = ? AND object = ? AND valid_to IS NULL",
            (now, subject, predicate, object),
        )
        self._conn.commit()

    def query(self, entity: str, as_of: str = None,
              direction: str = "both") -> list[dict]:
        """Return active triples for entity as_of (defaults to now)."""
        as_of = as_of or _utcnow()
        conditions = []
        params: list = []

        if direction in ("outgoing", "both"):
            conditions.append("subject = ?")
            params.append(entity)
        if direction in ("incoming", "both"):
            conditions.append("object = ?")
            params.append(entity)

        entity_clause = " OR ".join(conditions) if conditions else "1=1"
        sql = (
            f"SELECT * FROM triples "
            f"WHERE ({entity_clause}) "
            f"AND valid_from <= ? "
            f"AND (valid_to IS NULL OR valid_to > ?)"
        )
        params.extend([as_of, as_of])
        rows = self._conn.execute(sql, params).fetchall()
        return [dict(r) for r in rows]

    def timeline(self, entity: str = None) -> list[dict]:
        """All triples ordered by valid_from, optionally filtered by entity."""
        if entity:
            rows = self._conn.execute(
                "SELECT * FROM triples WHERE subject = ? OR object = ? ORDER BY valid_from",
                (entity, entity),
            ).fetchall()
        else:
            rows = self._conn.execute(
                "SELECT * FROM triples ORDER BY valid_from"
            ).fetchall()
        return [dict(r) for r in rows]

    def stats(self) -> dict:
        n_entities = self._conn.execute("SELECT COUNT(*) FROM entities").fetchone()[0]
        n_active = self._conn.execute(
            "SELECT COUNT(*) FROM triples WHERE valid_to IS NULL"
        ).fetchone()[0]
        n_total = self._conn.execute("SELECT COUNT(*) FROM triples").fetchone()[0]
        return {
            "entities": n_entities,
            "active_triples": n_active,
            "total_triples": n_total,
        }


# ---------------------------------------------------------------------------
# Class 4: LayeredRetrieval
# ---------------------------------------------------------------------------

class LayeredRetrieval:
    """L0-L3 retrieval with token budget caps."""

    MAX_L1_TOKENS = 900
    MAX_L1_DRAWERS = 15
    MAX_SNIPPET = 300

    def __init__(self, store: DrawerStore, identity_file: Path = None):
        self._store = store
        self._identity_file = identity_file
        self._identity_loaded = False
        self._identity_text = ""
        self._load_identity()

    def _load_identity(self) -> None:
        if self._identity_file and self._identity_file.exists():
            try:
                self._identity_text = self._identity_file.read_text(
                    encoding="utf-8", errors="replace"
                )
                self._identity_loaded = True
            except Exception:
                self._identity_text = self._fallback_identity()
        else:
            self._identity_text = self._fallback_identity()

    def _fallback_identity(self) -> str:
        return (
            "HELEN OS — constitutional AI governance layer.\n"
            "Non-sovereign. Informs proposals. Never admits truth.\n"
            "Bounded by 5 constitutional rules and 7 K-gates."
        )

    def wake_up(self, wing: str = "wing_helen") -> str:
        """L0 + L1. Called at /init. Budget-capped at MAX_L1_TOKENS."""
        # L0: identity
        l0 = f"[L0 IDENTITY]\n{self._identity_text.strip()}\n"
        token_budget = self.MAX_L1_TOKENS
        used = len(l0) // 4

        # L1: list_by_importance
        drawers = self._store.list_by_importance(wing, self.MAX_L1_DRAWERS)

        # Group by room
        rooms: dict[str, list] = {}
        for d in drawers:
            rooms.setdefault(d["room"], []).append(d)

        l1_parts = ["[L1 MEMORY]"]
        for room, items in rooms.items():
            l1_parts.append(f"  [{room}]")
            for item in items:
                snippet = item["content"][: self.MAX_SNIPPET]
                line = f"    • {snippet}"
                cost = len(line) // 4
                if used + cost > token_budget:
                    break
                l1_parts.append(line)
                used += cost

        l1 = "\n".join(l1_parts)
        return f"{l0}\n{l1}"

    def recall(self, wing: str, room: str = None, n: int = 10) -> str:
        """L2: on-demand recall by wing/room."""
        results = self._store.search("", wing=wing, room=room, n=n)
        if not results:
            return f"[L2 RECALL] No drawers found for wing={wing} room={room}"
        lines = [f"[L2 RECALL] wing={wing} room={room}"]
        for r in results:
            snippet = r["content"][: self.MAX_SNIPPET]
            lines.append(f"  ({r['source']}) {snippet}")
        return "\n".join(lines)

    def search(self, query: str, wing: str = None, n: int = 5) -> str:
        """L3: deep semantic search."""
        results = self._store.search(query, wing=wing, n=n)
        if not results:
            return f"[L3 SEARCH] No results for: {query!r}"
        lines = [f"[L3 SEARCH] query={query!r}"]
        for r in results:
            snippet = r["content"][: self.MAX_SNIPPET]
            lines.append(
                f"  sim={r['similarity']:.3f} imp={r['importance']:.1f} "
                f"[{r['wing']}/{r['room']}] {snippet}"
            )
        return "\n".join(lines)

    def status(self) -> dict:
        total = self._store.count()
        return {
            "total_drawers": total,
            "identity_loaded": self._identity_loaded,
            "layers": {
                "L0": "identity",
                "L1": "importance-ranked",
                "L2": "on-demand",
                "L3": "semantic",
            },
        }


# ---------------------------------------------------------------------------
# Class 5: HELENLibrarian (unified interface)
# ---------------------------------------------------------------------------

class HELENLibrarian:
    """
    HELEN's librarian. Informs proposals. Never admits truth.

    Below the sovereign kernel. Never calls GovernanceVM.
    Above the raw files. Provides structured retrieval.

    MemPalace patterns adapted:
    1. Transcript normalization (multi-format → clean chunks)
    2. Conversation/file miners (chunks → DrawerStore)
    3. Entity registry + invalidation (temporal knowledge graph)
    4. Layered retrieval L0-L3 (budget-capped, scored)
    """

    HELEN_DB = Path.home() / ".helen" / "librarian.db"
    HELEN_IDENTITY = Path.home() / ".helen" / "identity.txt"

    def __init__(
        self,
        db_path: Path = None,
        ollama_url: str = None,
        identity_file: Path = None,
    ):
        db = db_path or self.HELEN_DB
        db.parent.mkdir(parents=True, exist_ok=True)
        self.store = DrawerStore(db, ollama_url or "http://localhost:11434")
        self.registry = EntityRegistry(db)
        self.normalizer = TranscriptNormalizer()
        self.retrieval = LayeredRetrieval(
            self.store, identity_file or self.HELEN_IDENTITY
        )

    # ------------------------------------------------------------------
    # Ingestion
    # ------------------------------------------------------------------

    def ingest_session(
        self, ndjson_path: Path, wing: str = "wing_helen", room: str = "session",
        max_seconds: float | None = None, limit: int | None = None,
    ) -> int:
        """Normalize + mine a chat session file. Returns number of drawers created.

        store.add() does an O(n) keyword-overlap dedup scan over every existing
        drawer (embeddings are off unless `nomic-embed-text` is pulled), so
        ingesting a long file against a large DB is O(n²) and can stall boot.
        `max_seconds` bounds the wall-clock cost; `limit` bounds the count.
        Newest turns are processed first so a bounded run keeps recent memory.
        """
        import time
        turns = self.normalizer.normalize(ndjson_path)
        if max_seconds is not None or limit is not None:
            turns = list(reversed(turns))  # newest-first under a budget
        deadline = (time.monotonic() + max_seconds) if max_seconds else None
        count = 0
        for turn in turns:
            if deadline is not None and time.monotonic() > deadline:
                break
            if limit is not None and count >= limit:
                break
            if turn["content"].strip():
                src = f"{ndjson_path.name}:{turn.get('ts', '')}"
                importance = 1.2 if turn["role"] == "helen" else 1.0
                drawer_id = self.store.add(turn["content"], wing, room, src, importance)
                if drawer_id:
                    count += 1
        return count

    def ingest_file(
        self, path: Path, wing: str = "wing_helen", room: str = "files"
    ) -> int:
        """Chunk a file into ~500-char drawers. Returns number created."""
        text = path.read_text(encoding="utf-8", errors="replace")
        chunks = []
        chunk_size = 500
        for i in range(0, len(text), chunk_size):
            chunk = text[i : i + chunk_size].strip()
            if chunk:
                chunks.append(chunk)

        count = 0
        src = str(path.name)
        for chunk in chunks:
            drawer_id = self.store.add(chunk, wing, room, src, 1.0)
            if drawer_id:
                count += 1
        return count

    # ------------------------------------------------------------------
    # Entity / knowledge graph
    # ------------------------------------------------------------------

    def register_entity(self, name: str, entity_type: str = "unknown") -> str:
        return self.registry.register(name, entity_type)

    def add_fact(
        self,
        subject: str,
        predicate: str,
        object: str,
        valid_from: str = None,
        source: str = "",
    ) -> str:
        return self.registry.add_fact(
            subject, predicate, object, valid_from, source=source
        )

    def invalidate_fact(
        self, subject: str, predicate: str, object: str
    ) -> None:
        self.registry.invalidate(subject, predicate, object)

    def query_entity(self, entity: str, as_of: str = None) -> list[dict]:
        return self.registry.query(entity, as_of)

    # ------------------------------------------------------------------
    # Retrieval (informs proposals, never admits)
    # ------------------------------------------------------------------

    def wake_up(self, wing: str = "wing_helen") -> str:
        return self.retrieval.wake_up(wing)

    def recall(self, wing: str = "wing_helen", room: str = None, n: int = 10) -> str:
        return self.retrieval.recall(wing, room, n)

    def search(self, query: str, wing: str = None, n: int = 5) -> str:
        return self.retrieval.search(query, wing, n)

    def status(self) -> dict:
        return {**self.retrieval.status(), "registry": self.registry.stats()}
