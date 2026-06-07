#!/usr/bin/env python3
"""
helen_local_rag.py — code-aware corpus index over HELEN's own organs.

WHY THIS EXISTS (operator's order: RAG first, fine-tune later):
  Fine-tuning teaches style; RAG gives exact CURRENT code. For HELEN, exactness
  matters more — a fine-tuned model still hallucinates wrong repo_root, wrong
  function signature, wrong tool schema. RAG retrieves the real thing with a
  citation: "_skill_write_file -> helen_skills.py:488, args(path, content, append)".

  Dependency-free (stdlib only): no embeddings, no vector DB, no network. Builds
  a symbol+chunk index over .py/.md/.json/.ndjson/.txt and answers:
    - where is <symbol> defined?  -> file:line + signature
    - what is the signature of <fn>? -> def line
    - keyword search -> ranked chunks with file:line citations

  This is the L0 (exact symbol) + L1 (keyword chunk) layer. Embedding retrieval
  (L2/L3) can layer on later via the existing helen_librarian; this gives precise,
  cited, zero-dependency answers TODAY.

USAGE:
    python3 helen_local_rag.py index [REPO_ROOT]      # build .helen_rag_index.json
    python3 helen_local_rag.py sig _skill_write_file  # exact symbol -> file:line+sig
    python3 helen_local_rag.py ask "where is extract_action defined"
    python3 helen_local_rag.py search "tool schema"   # keyword -> cited chunks

  In a runtime, import and call:
    from helen_local_rag import RagIndex
    idx = RagIndex.load_or_build(repo_root)
    print(idx.signature("_skill_write_file"))   # cited answer string

authority: false · read-only retrieval · cites real files; never fabricates a
path or signature (if a symbol is absent, says so).
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

INDEX_NAME = ".helen_rag_index.json"
CORPUS_EXT = {".py", ".md", ".json", ".ndjson", ".txt"}
SKIP_PARTS = {"__pycache__", ".git", "node_modules", ".venv"}

# Python def/class with captured signature line.
_PY_DEF = re.compile(r"^\s*(def|class)\s+([A-Za-z_][A-Za-z0-9_]*)\s*(\(.*)?")


def _iter_corpus(root: Path, max_depth: int = 6):
    root = root.resolve()
    for p in root.rglob("*"):
        if not p.is_file():
            continue
        if p.suffix not in CORPUS_EXT:
            continue
        if any(part in SKIP_PARTS for part in p.parts):
            continue
        try:
            if len(p.relative_to(root).parts) > max_depth:
                continue
        except ValueError:
            continue
        yield p


class RagIndex:
    def __init__(self, repo_root: Path, symbols: dict, chunks: list):
        self.repo_root = repo_root
        self.symbols = symbols   # name -> list of {file, line, signature, kind}
        self.chunks = chunks     # list of {file, line, text}

    # ---- build ----
    @classmethod
    def build(cls, repo_root: Path) -> "RagIndex":
        repo_root = repo_root.resolve()
        symbols: dict[str, list[dict]] = {}
        chunks: list[dict] = []
        for p in _iter_corpus(repo_root):
            rel = str(p.relative_to(repo_root))
            try:
                lines = p.read_text(encoding="utf-8", errors="replace").splitlines()
            except Exception:
                continue
            # Python symbols
            if p.suffix == ".py":
                for i, line in enumerate(lines, 1):
                    m = _PY_DEF.match(line)
                    if m:
                        kind, name = m.group(1), m.group(2)
                        sig = line.strip()
                        symbols.setdefault(name, []).append(
                            {"file": rel, "line": i, "signature": sig, "kind": kind}
                        )
            # Chunk every file (40-line windows) for keyword search
            for start in range(0, len(lines), 40):
                window = "\n".join(lines[start:start + 40]).strip()
                if window:
                    chunks.append({"file": rel, "line": start + 1, "text": window})
        return cls(repo_root, symbols, chunks)

    @classmethod
    def load_or_build(cls, repo_root: Path) -> "RagIndex":
        repo_root = repo_root.resolve()
        idxp = repo_root / INDEX_NAME
        if idxp.exists():
            try:
                d = json.loads(idxp.read_text(encoding="utf-8"))
                return cls(repo_root, d["symbols"], d["chunks"])
            except Exception:
                pass
        idx = cls.build(repo_root)
        idx.save()
        return idx

    def save(self) -> Path:
        idxp = self.repo_root / INDEX_NAME
        idxp.write_text(json.dumps(
            {"repo_root": str(self.repo_root),
             "symbols": self.symbols, "chunks": self.chunks},
            ensure_ascii=False), encoding="utf-8")
        return idxp

    # ---- query ----
    def signature(self, symbol: str) -> str:
        """Exact symbol -> cited file:line + signature. Never fabricates."""
        hits = self.symbols.get(symbol)
        if not hits:
            # case-insensitive fallback
            low = symbol.lower()
            hits = []
            for name, defs in self.symbols.items():
                if name.lower() == low:
                    hits = defs
                    break
        if not hits:
            return f"NOT FOUND: no definition of {symbol!r} in the index. (Run `index` if stale.)"
        out = [f"{symbol} — {len(hits)} definition(s):"]
        for h in hits:
            out.append(f"  {h['file']}:{h['line']}  [{h['kind']}]  {h['signature']}")
        return "\n".join(out)

    def search(self, query: str, k: int = 5) -> str:
        """Keyword chunk search -> ranked cited results."""
        terms = [t.lower() for t in re.findall(r"\w+", query) if len(t) > 1]
        if not terms:
            return "empty query"
        scored = []
        for c in self.chunks:
            tl = c["text"].lower()
            score = sum(tl.count(t) for t in terms)
            if score:
                scored.append((score, c))
        scored.sort(key=lambda x: -x[0])
        if not scored:
            return f"no chunks match {query!r}"
        out = [f"top {min(k, len(scored))} for {query!r}:"]
        for score, c in scored[:k]:
            first = c["text"].splitlines()[0][:80]
            out.append(f"  [{score}] {c['file']}:{c['line']}  {first!r}")
        return "\n".join(out)

    def ask(self, question: str) -> str:
        """Heuristic: 'where is X defined' / 'signature of X' -> symbol lookup;
        else keyword search. Always cites."""
        m = re.search(r"(?:where is|signature of|define[ds]?|location of)\s+([A-Za-z_][A-Za-z0-9_]*)",
                      question, re.I)
        if m:
            return self.signature(m.group(1))
        # last identifier-looking token
        ids = re.findall(r"[A-Za-z_][A-Za-z0-9_]{2,}", question)
        if ids and ids[-1] in self.symbols:
            return self.signature(ids[-1])
        return self.search(question)

    def stats(self) -> str:
        return (f"index: {len(self.symbols)} symbols, {len(self.chunks)} chunks, "
                f"root={self.repo_root}")


def _main(argv: list[str]) -> int:
    if not argv:
        print("usage: helen_local_rag.py [index|sig|ask|search|stats] ...", file=sys.stderr)
        return 2
    cmd = argv[0]
    # repo_root: arg for index, else cwd's index location
    if cmd == "index":
        root = Path(argv[1]) if len(argv) > 1 else Path.cwd()
        idx = RagIndex.build(root)
        p = idx.save()
        print(f"built {p}")
        print(idx.stats())
        return 0
    root = Path.cwd()
    idx = RagIndex.load_or_build(root)
    if cmd == "sig":
        print(idx.signature(argv[1]))
    elif cmd == "ask":
        print(idx.ask(" ".join(argv[1:])))
    elif cmd == "search":
        print(idx.search(" ".join(argv[1:])))
    elif cmd == "stats":
        print(idx.stats())
    else:
        print(f"unknown command: {cmd}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(_main(sys.argv[1:]))
