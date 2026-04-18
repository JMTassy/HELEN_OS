"""
HELEN KNOWLEDGE_ENGINE_V1 — Governed retrieval from user corpus.

NOT fine-tuning. NOT RAG. This is RAK: Retrieval-Augmented Kernel.

Differences from standard RAG:
  - Retrieval is governed (authority=false)
  - Retrieval is receipted (every access logged with hashes)
  - Retrieval is replayable (same query → same results → verifiable)
  - Tags are first-class (plugins become query filters, not training data)

Pipeline:
  Corpus → Index → Tag Graph → Retrieval (READ only) → Cognition context

Usage:
    from helen_os.knowledge.engine import KnowledgeEngine
    engine = KnowledgeEngine()
    engine.ingest_corpus("/path/to/PLUGINS_JMT")
    results = engine.retrieve("kernel design", tags=["pluginHELEN"], k=5)
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import time
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _now_utc() -> str:
    import datetime
    return datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "Z")


KNOWLEDGE_DIR = Path(__file__).parent
CORPUS_PATH = KNOWLEDGE_DIR / "corpus.json"
TAG_GRAPH_PATH = KNOWLEDGE_DIR / "tag_graph.json"
ACCESS_LOG_PATH = KNOWLEDGE_DIR / "access_log.ndjson"

SKIP_DIRS = {"node_modules", ".git", ".venv", "__pycache__", "worktrees"}
SUPPORTED_EXTS = {".md", ".txt", ".pdf", ".py", ".json", ".ndjson"}

# Tag extraction pattern: #word or #wordWord or #word_word
TAG_RE = re.compile(r'#([A-Za-z][A-Za-z0-9_]{2,})')


# ─── Knowledge Unit ──────────────────────────────────────────────────────────

@dataclass
class KnowledgeUnit:
    id: str
    tags: List[str]
    content: str
    source_file: str
    hash: str
    chunk_index: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "tags": self.tags,
            "content": self.content[:3000],
            "source_file": self.source_file,
            "hash": self.hash,
            "chunk_index": self.chunk_index,
        }


# ─── Tag Graph ────────────────────────────────────────────────────────────────

@dataclass
class TagGraph:
    tag_to_units: Dict[str, List[str]] = field(default_factory=lambda: defaultdict(list))
    cooccurrence: Dict[str, Dict[str, int]] = field(default_factory=lambda: defaultdict(lambda: defaultdict(int)))
    tag_frequency: Dict[str, int] = field(default_factory=lambda: defaultdict(int))

    def add_unit(self, unit_id: str, tags: List[str]):
        for tag in tags:
            self.tag_to_units[tag].append(unit_id)
            self.tag_frequency[tag] += 1
        for i, a in enumerate(tags):
            for b in tags[i+1:]:
                self.cooccurrence[a][b] += 1
                self.cooccurrence[b][a] += 1

    def get_related_tags(self, tag: str, top_k: int = 5) -> List[Tuple[str, int]]:
        if tag not in self.cooccurrence:
            return []
        related = sorted(self.cooccurrence[tag].items(), key=lambda x: -x[1])
        return related[:top_k]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tag_to_units": dict(self.tag_to_units),
            "tag_frequency": dict(self.tag_frequency),
            "cooccurrence": {k: dict(v) for k, v in self.cooccurrence.items()},
        }

    @classmethod
    def from_dict(cls, d: Dict) -> "TagGraph":
        g = cls()
        g.tag_to_units = defaultdict(list, d.get("tag_to_units", {}))
        g.tag_frequency = defaultdict(int, d.get("tag_frequency", {}))
        raw = d.get("cooccurrence", {})
        g.cooccurrence = defaultdict(lambda: defaultdict(int))
        for k, v in raw.items():
            for k2, count in v.items():
                g.cooccurrence[k][k2] = count
        return g


# ─── Access Receipt ──────────────────────────────────────────────────────────

@dataclass
class AccessReceipt:
    query: str
    tags_filter: List[str]
    result_ids: List[str]
    result_hashes: List[str]
    mode: str
    timestamp: str = ""
    authority: str = "NONE"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "KNOWLEDGE_ACCESS_V1",
            "query": self.query,
            "tags_filter": self.tags_filter,
            "result_ids": self.result_ids,
            "result_hashes": self.result_hashes,
            "mode": self.mode,
            "timestamp": self.timestamp or _now_utc(),
            "authority": self.authority,
        }


# ─── Knowledge Engine ────────────────────────────────────────────────────────

class KnowledgeEngine:
    def __init__(self):
        self.units: Dict[str, KnowledgeUnit] = {}
        self.tag_graph = TagGraph()
        self._load()

    def _load(self):
        if CORPUS_PATH.exists():
            data = json.loads(CORPUS_PATH.read_text())
            for u in data.get("units", []):
                unit = KnowledgeUnit(**u)
                self.units[unit.id] = unit
        if TAG_GRAPH_PATH.exists():
            data = json.loads(TAG_GRAPH_PATH.read_text())
            self.tag_graph = TagGraph.from_dict(data)

    def _save(self):
        KNOWLEDGE_DIR.mkdir(parents=True, exist_ok=True)
        CORPUS_PATH.write_text(json.dumps({
            "version": 1,
            "total_units": len(self.units),
            "units": [u.to_dict() for u in self.units.values()],
        }, indent=2, ensure_ascii=False) + "\n")
        TAG_GRAPH_PATH.write_text(json.dumps(self.tag_graph.to_dict(), indent=2, ensure_ascii=False) + "\n")

    def _log_access(self, receipt: AccessReceipt):
        ACCESS_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with ACCESS_LOG_PATH.open("a") as f:
            f.write(json.dumps(receipt.to_dict(), ensure_ascii=False) + "\n")

    def _extract_text(self, path: Path) -> Optional[str]:
        try:
            if path.suffix == ".pdf":
                r = subprocess.run(["pdftotext", "-layout", str(path), "-"],
                                 capture_output=True, text=True, timeout=30)
                return r.stdout if r.returncode == 0 else None
            else:
                return path.read_text(encoding="utf-8", errors="ignore")
        except:
            return None

    def _extract_tags(self, text: str, filename: str) -> List[str]:
        tags = set()
        # From content
        for match in TAG_RE.findall(text):
            tags.add(match.lower())
        # From filename
        for match in TAG_RE.findall(filename):
            tags.add(match.lower())
        # Infer from filename patterns
        fname = filename.lower()
        if "helen" in fname: tags.add("pluginhelen")
        if "riemann" in fname: tags.add("pluginriemann")
        if "swarm" in fname: tags.add("pluginswarm")
        if "oracle" in fname: tags.add("pluginoracle")
        if "conquest" in fname: tags.add("pluginconquest")
        if "agi" in fname: tags.add("pluginagi")
        if "legoracle" in fname: tags.add("pluginlegoracle")
        return sorted(tags)

    def _chunk(self, text: str, size: int = 800, overlap: int = 100) -> List[str]:
        if len(text) <= size:
            return [text]
        chunks = []
        start = 0
        while start < len(text):
            end = start + size
            chunk = text[start:end]
            if chunk.strip():
                chunks.append(chunk)
            start = end - overlap
        return chunks

    # ── Ingest ────────────────────────────────────────────────────────────────

    def ingest_corpus(self, source_path: str, max_files: int = 500) -> int:
        """Ingest files into knowledge units. Returns count of new units."""
        src = Path(source_path).expanduser()
        existing_hashes = {u.hash for u in self.units.values()}
        files: List[Path] = []

        if src.is_file():
            files = [src]
        elif src.is_dir():
            for f in src.rglob("*"):
                if f.is_file() and f.suffix in SUPPORTED_EXTS:
                    if not any(skip in f.parts for skip in SKIP_DIRS):
                        files.append(f)

        files = files[:max_files]
        new_count = 0

        for f in files:
            text = self._extract_text(f)
            if not text or len(text.strip()) < 50:
                continue

            tags = self._extract_tags(text, f.name)
            chunks = self._chunk(text)

            for i, chunk in enumerate(chunks):
                h = _sha256(chunk)[:16]
                if h in existing_hashes:
                    continue

                unit_id = f"{f.stem}_{i:03d}"
                unit = KnowledgeUnit(
                    id=unit_id,
                    tags=tags,
                    content=chunk[:3000],
                    source_file=str(f),
                    hash=h,
                    chunk_index=i,
                )
                self.units[unit_id] = unit
                self.tag_graph.add_unit(unit_id, tags)
                existing_hashes.add(h)
                new_count += 1

        self._save()
        return new_count

    # ── Retrieve ──────────────────────────────────────────────────────────────

    def retrieve(
        self,
        query: str,
        tags: Optional[List[str]] = None,
        k: int = 5,
        mode: str = "keyword",
    ) -> List[KnowledgeUnit]:
        """
        Typed retrieval with tag filtering and receipt logging.

        Modes:
          - "keyword": simple text match (fast, no API)
          - "tag": return units matching ALL specified tags
          - "hybrid": keyword + tag boost
        """
        candidates = list(self.units.values())

        # Tag filter
        if tags:
            tag_set = {t.lower() for t in tags}
            tag_unit_ids: Set[str] = set()
            for tag in tag_set:
                for uid in self.tag_graph.tag_to_units.get(tag, []):
                    tag_unit_ids.add(uid)
            if tag_unit_ids:
                candidates = [u for u in candidates if u.id in tag_unit_ids]

        # Score
        query_lower = query.lower()
        query_words = set(query_lower.split())
        scored = []
        for unit in candidates:
            content_lower = unit.content.lower()
            # Keyword score
            word_hits = sum(1 for w in query_words if w in content_lower)
            # Exact phrase bonus
            phrase_bonus = 2.0 if query_lower in content_lower else 0
            # Tag relevance bonus
            tag_bonus = 0
            if tags:
                tag_bonus = sum(0.5 for t in tags if t.lower() in [ut.lower() for ut in unit.tags])
            score = word_hits + phrase_bonus + tag_bonus
            if score > 0:
                scored.append((score, unit))

        scored.sort(key=lambda x: -x[0])
        results = [unit for _, unit in scored[:k]]

        # Log access receipt
        receipt = AccessReceipt(
            query=query,
            tags_filter=tags or [],
            result_ids=[u.id for u in results],
            result_hashes=[u.hash for u in results],
            mode=mode,
        )
        self._log_access(receipt)

        return results

    # ── Stats ─────────────────────────────────────────────────────────────────

    def stats(self) -> Dict[str, Any]:
        return {
            "total_units": len(self.units),
            "total_tags": len(self.tag_graph.tag_frequency),
            "top_tags": sorted(self.tag_graph.tag_frequency.items(), key=lambda x: -x[1])[:15],
            "files_indexed": len(set(u.source_file for u in self.units.values())),
        }

    def tag_map(self) -> Dict[str, int]:
        return dict(sorted(self.tag_graph.tag_frequency.items(), key=lambda x: -x[1]))
