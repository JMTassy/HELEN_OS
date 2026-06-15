"""
kb_scan — local knowledge base scanner for HELEN media assets.

Creates ~/HELEN_KNOWLEDGE_BASE/ and emits:
  manifests/local_manifest.json  — full index of all scanned assets
  manifests/canonical.json       — helen_*-named canonical assets only
  ledger.ndjson                  — append-only scan log

Usage:
    python3 tools/kb_scan.py
    python3 tools/kb_scan.py --src ~/Desktop/HELEN_OS_PICS ~/Music ~/Movies
    python3 tools/kb_scan.py --out ~/MY_KB --dry-run

Non-sovereign: writes to KB_ROOT only, never to the SOT.
No pip installs required. Uses ffprobe if available (graceful degradation).
"""

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from datetime import datetime, timezone

# ── Configuration ──────────────────────────────────────────────────────────────

KB_ROOT_DEFAULT = Path.home() / "HELEN_KNOWLEDGE_BASE"

DEFAULT_SOURCES = [
    Path.home() / "Desktop" / "HELEN_OS_PICS",
    Path.home() / "Music",
    Path.home() / "Movies",
    Path.home() / "Documents",
]

EXTENSIONS = {
    "image":    {".png", ".jpg", ".jpeg", ".webp", ".gif", ".tiff", ".bmp", ".heic"},
    "video":    {".mp4", ".mov", ".avi", ".mkv", ".webm", ".m4v"},
    "audio":    {".mp3", ".wav", ".m4a", ".flac", ".ogg", ".aac"},
    "document": {".pdf", ".md", ".txt", ".docx", ".pages"},
    "code":     {".py", ".js", ".ts", ".sh", ".json", ".yaml", ".ndjson"},
}

# HELEN canonical naming: helen_<theme>_<descriptor>_<NN>.ext
# Index _NN is REQUIRED to distinguish canonical from source files like helen_talk.py
HELEN_CANONICAL_RE = re.compile(
    r"^helen_(?P<theme>[a-z0-9]+)(?:_(?P<descriptor>[a-z0-9]+))?_(?P<index>\d{2})$",
    re.IGNORECASE,
)

# Directories to skip during recursive scan
SKIP_DIRS = {
    ".git", "node_modules", "__pycache__", ".venv", "venv",
    ".venv-gates", ".Trash", "Library", "GitHub", "worktrees",
}

# Era taxonomy from oracle_town/skills/video/library/taxonomy.md
ERA_TAGS = {
    "cyberpunk", "medieval", "renaissance", "modern", "ww2",
    "french_revolution", "pyramids",
}
SEMANTIC_TAGS = {
    "emotions", "metaverse", "cathedral", "conquest", "dossier",
    "portrait", "half_body", "full_body", "green_screen", "cinematic",
    "ritual", "abstract",
}


# ── Utilities ──────────────────────────────────────────────────────────────────

def sha16(path: Path) -> str:
    h = hashlib.sha256()
    try:
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                h.update(chunk)
    except (OSError, PermissionError):
        return "err"
    return h.hexdigest()[:16]


def detect_type(path: Path) -> str:
    ext = path.suffix.lower()
    for kind, exts in EXTENSIONS.items():
        if ext in exts:
            return kind
    return "other"


def probe_media(path: Path) -> dict:
    """Run ffprobe to get duration and dimensions. Returns {} on failure."""
    try:
        cmd = [
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration:stream=width,height",
            "-of", "json", str(path),
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        if result.returncode != 0:
            return {}
        data = json.loads(result.stdout)
        out = {}
        fmt = data.get("format", {})
        if "duration" in fmt:
            out["duration_s"] = round(float(fmt["duration"]), 2)
        streams = data.get("streams", [{}])
        s = streams[0] if streams else {}
        if "width" in s:
            out["width"] = s["width"]
        if "height" in s:
            out["height"] = s["height"]
        return out
    except (FileNotFoundError, subprocess.TimeoutExpired, json.JSONDecodeError):
        return {}


def tag_asset(path: Path, kind: str) -> list[str]:
    """Infer semantic tags from filename + path."""
    tags = [kind]
    stem = path.stem.lower()

    # Heuristic tagging from path/filename tokens
    text = stem + " " + " ".join(p.lower() for p in path.parts[-4:])

    # HELEN canonical: strict _NN suffix (promoted assets)
    m = HELEN_CANONICAL_RE.match(stem)
    if m and kind == "image":
        tags.append("helen")
        tags.append("helen_canonical")
        theme = (m.group("theme") or "").lower()
        descriptor = (m.group("descriptor") or "").lower()
        for t in [theme, descriptor]:
            if t in ERA_TAGS:
                tags.append("era:" + t)
            if t in SEMANTIC_TAGS:
                tags.append("semantic:" + t)
            if t:
                tags.append(t)
    elif kind == "image" and re.match(r"^helen_", stem, re.IGNORECASE):
        # Pre-convention HELEN images: tagged as source candidates, not yet canonical
        tags.append("helen")
        tags.append("helen_source")  # candidate for promotion
        for era in ERA_TAGS:
            if era in text:
                tags.append("era:" + era)
        for sem in SEMANTIC_TAGS:
            if sem in text:
                tags.append("semantic:" + sem)
        # Infer theme from name parts
        parts = stem.split("_")[1:]  # drop "helen"
        for p in parts:
            if p in ERA_TAGS or p in SEMANTIC_TAGS:
                tags.append(p)
    else:
        # Generic heuristic tagging
        if "helen" in text:
            tags.append("helen")
        for era in ERA_TAGS:
            if era in text:
                tags.append("era:" + era)
        for sem in SEMANTIC_TAGS:
            if sem in text:
                tags.append("semantic:" + sem)
        if kind == "audio":
            if "ritual" in text or "dark" in text:
                tags.append("mood:ritual")
            elif "epic" in text:
                tags.append("mood:epic")
            elif "soft" in text or "calm" in text or "oracle" in text:
                tags.append("mood:calm")

    return list(dict.fromkeys(tags))  # dedupe, preserve order


def is_helen_canonical(path: Path, kind: str = "") -> bool:
    """True only for image files matching helen_<theme>_<descriptor>_<NN>.ext."""
    if kind and kind != "image":
        return False
    return bool(HELEN_CANONICAL_RE.match(path.stem))


# ── Scanner ────────────────────────────────────────────────────────────────────

def scan_source(src: Path, dry_run: bool = False) -> list[dict]:
    if not src.exists():
        print(f"  [skip] not found: {src}", file=sys.stderr)
        return []

    entries = []
    for root, _dirs, files in os.walk(src):
        # Skip hidden dirs and known noise dirs
        _dirs[:] = [d for d in _dirs if not d.startswith(".") and d not in SKIP_DIRS]
        for fname in files:
            if fname.startswith("."):
                continue
            fpath = Path(root) / fname
            kind = detect_type(fpath)
            if kind == "other":
                continue

            size = 0
            try:
                size = fpath.stat().st_size
            except OSError:
                continue

            entry = {
                "id": None,  # filled after sort
                "path": str(fpath),
                "name": fpath.name,
                "type": kind,
                "ext": fpath.suffix.lower(),
                "size_bytes": size,
                "sha16": sha16(fpath) if not dry_run else "dry",
                "tags": tag_asset(fpath, kind),
                "helen_canonical": is_helen_canonical(fpath, kind),
                "source_dir": str(src),
                "scanned_at": datetime.now(timezone.utc).isoformat(),
            }

            # Media probing
            if kind in ("video", "audio") and not dry_run:
                media_meta = probe_media(fpath)
                entry.update(media_meta)

            entries.append(entry)
            print(f"  [{kind:8s}] {fpath.name}")

    return entries


# ── KB structure setup ─────────────────────────────────────────────────────────

def setup_kb(kb_root: Path) -> None:
    dirs = [
        kb_root / "manifests",
        kb_root / "hashes",
        kb_root / "receipts",
        kb_root / "inbox",
        kb_root / "canonical" / "helen",
        kb_root / "canonical" / "conquest",
        kb_root / "canonical" / "wulmoji",
    ]
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Scan local media into HELEN knowledge base.")
    parser.add_argument(
        "--src", action="append", type=Path,
        help="Source directory to scan (repeatable: --src dir1 --src dir2)",
    )
    parser.add_argument(
        "--out", type=Path, default=KB_ROOT_DEFAULT,
        help=f"KB root directory (default: {KB_ROOT_DEFAULT})",
    )
    parser.add_argument("--dry-run", action="store_true", help="Scan but do not write outputs")
    args = parser.parse_args()

    sources = [Path(s).expanduser() for s in args.src] if args.src else DEFAULT_SOURCES
    kb_root = args.out.expanduser()

    print(f"kb_scan — KB root: {kb_root}")
    print(f"Sources ({len(sources)}):")
    for s in sources:
        print(f"  {s}")
    print()

    if not args.dry_run:
        setup_kb(kb_root)

    all_entries = []
    for src in sources:
        print(f"Scanning: {src}")
        entries = scan_source(src, dry_run=args.dry_run)
        all_entries.extend(entries)
        print(f"  → {len(entries)} assets\n")

    # Assign deterministic IDs
    all_entries.sort(key=lambda e: e["path"])
    for i, entry in enumerate(all_entries):
        entry["id"] = f"asset_{i:04d}"

    # Summary
    type_counts = {}
    helen_count = 0
    for e in all_entries:
        type_counts[e["type"]] = type_counts.get(e["type"], 0) + 1
        if e["helen_canonical"]:
            helen_count += 1

    print("Summary:")
    for kind, count in sorted(type_counts.items()):
        print(f"  {kind:12s}: {count}")
    print(f"  {'canonical':12s}: {helen_count} (helen_* named)")
    print(f"  {'total':12s}: {len(all_entries)}")

    if args.dry_run:
        print("\n[dry-run] no files written.")
        return

    # Write manifests
    manifest_path = kb_root / "manifests" / "kb_manifest.json"
    manifest_path.write_text(
        json.dumps({"schema": "kb_manifest_v1", "entries": all_entries}, indent=2, ensure_ascii=False)
    )
    print(f"\nManifest  → {manifest_path}")

    canonical_entries = [e for e in all_entries if e["helen_canonical"]]
    canonical_path = kb_root / "manifests" / "canonical.json"
    canonical_path.write_text(
        json.dumps({"schema": "kb_canonical_v1", "entries": canonical_entries}, indent=2, ensure_ascii=False)
    )
    print(f"Canonical → {canonical_path}  ({len(canonical_entries)} entries)")

    # Type-split catalogs
    for kind in ("image", "audio", "video", "document"):
        typed = [e for e in all_entries if e["type"] == kind]
        if typed:
            cat_path = kb_root / "manifests" / f"{kind}_catalog.json"
            cat_path.write_text(
                json.dumps({"schema": f"kb_{kind}_catalog_v1", "entries": typed}, indent=2, ensure_ascii=False)
            )
            print(f"{kind:9s} → {cat_path}  ({len(typed)} entries)")

    # Write sha256 hash index: {sha16 → [path, name, type, tags]}
    hash_index = {}
    for e in all_entries:
        h = e["sha16"]
        if h and h != "dry":
            hash_index[h] = {"path": e["path"], "name": e["name"], "type": e["type"], "tags": e["tags"]}
    hash_index_path = kb_root / "hashes" / "sha256_index.json"
    hash_index_path.write_text(
        json.dumps({"schema": "kb_hash_index_v1", "count": len(hash_index), "index": hash_index},
                   indent=2, ensure_ascii=False)
    )
    print(f"Hashes    → {hash_index_path}  ({len(hash_index)} entries)")

    # Emit scan receipt to receipts/scan_receipts.jsonl
    manifest_sha = hashlib.sha256(manifest_path.read_bytes()).hexdigest()
    receipt = {
        "schema": "KB_SCAN_RECEIPT_V1",
        "op": "SCAN",
        "scanned_at": datetime.now(timezone.utc).isoformat(),
        "sources": [str(s) for s in sources],
        "total": len(all_entries),
        "by_type": type_counts,
        "canonical_count": len(canonical_entries),
        "manifest_path": str(manifest_path),
        "manifest_sha256": manifest_sha,
        "authority": "NON_SOVEREIGN",
        "ledger_effect": "NONE",
    }
    receipts_path = kb_root / "receipts" / "scan_receipts.jsonl"
    with open(receipts_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(receipt, ensure_ascii=False) + "\n")
    print(f"Receipt   → {receipts_path}  (appended)")

    # Append to ledger
    ledger_path = kb_root / "ledger.ndjson"
    ledger_entry = {
        "op": "SCAN_V1",
        "scanned_at": receipt["scanned_at"],
        "sources": [str(s) for s in sources],
        "total": len(all_entries),
        "canonical": len(canonical_entries),
        "by_type": type_counts,
        "manifest": str(manifest_path),
        "manifest_sha256": manifest_sha,
    }
    with open(ledger_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(ledger_entry, ensure_ascii=False) + "\n")
    print(f"Ledger    → {ledger_path}  (appended)")

    print("\n🏁 kb_scan complete.")
    print(f"   To retrieve: load {manifest_path}")
    print(f"   HELEN canonical assets: {len(canonical_entries)}")
    print()
    print("Retrieval examples:")
    print("  python3 -c \"import json; m=json.load(open('~/HELEN_KNOWLEDGE_BASE/manifests/canonical.json')); [print(e['path']) for e in m['entries'] if 'emotions' in e['tags']]\"")


if __name__ == "__main__":
    main()
