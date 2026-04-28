#!/usr/bin/env python3
"""
HELEN media inventory v1 — read-only walk of operator Desktop + Downloads.

Surfaces all video/audio/image assets with metadata. Zero API calls. Zero spend.
Output: /tmp/helen_media_inventory_v1.json (one record per file)
Plus a summary printed to stdout (counts, top-largest, top-most-recent).

Non-sovereign tool. Does NOT classify content, does NOT call any API,
does NOT promote any media to canon. Pure inventory.
"""
import json
import os
import subprocess
import sys
import time
from pathlib import Path

ROOTS = [Path.home() / "Desktop", Path.home() / "Downloads"]
MAX_DEPTH = 4

VIDEO_EXTS = {".mp4", ".mov", ".m4v", ".avi", ".mkv", ".webm"}
AUDIO_EXTS = {".mp3", ".wav", ".m4a", ".aac", ".flac", ".ogg", ".opus"}
IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".heic", ".webp", ".tiff", ".bmp"}
ALL_MEDIA = VIDEO_EXTS | AUDIO_EXTS | IMAGE_EXTS

SKIP_DIR_NAMES = {
    "__pycache__", "node_modules", ".git", ".Trash", ".npm", ".cache",
    ".pytest_cache", ".venv", "venv", ".idea", ".vscode",
}
# .app, .photoslibrary, .bundle — opaque macOS bundles
SKIP_BUNDLE_SUFFIXES = {".app", ".photoslibrary", ".bundle", ".framework"}


def media_class(ext: str) -> str:
    if ext in VIDEO_EXTS:
        return "video"
    if ext in AUDIO_EXTS:
        return "audio"
    if ext in IMAGE_EXTS:
        return "image"
    return "other"


def probe_duration(path: Path) -> float | None:
    """Get duration in seconds for video/audio via ffprobe. None on failure."""
    try:
        r = subprocess.run(
            [
                "ffprobe", "-v", "error",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1",
                str(path),
            ],
            capture_output=True, text=True, timeout=10,
        )
        if r.returncode == 0 and r.stdout.strip():
            return round(float(r.stdout.strip()), 2)
    except Exception:
        pass
    return None


def probe_image_dimensions(path: Path) -> tuple[int, int] | None:
    """Get image dimensions via `file` or sips. None on failure."""
    try:
        r = subprocess.run(
            ["sips", "-g", "pixelWidth", "-g", "pixelHeight", str(path)],
            capture_output=True, text=True, timeout=5,
        )
        if r.returncode == 0:
            w = h = None
            for line in r.stdout.splitlines():
                line = line.strip()
                if line.startswith("pixelWidth:"):
                    w = int(line.split(":", 1)[1].strip())
                elif line.startswith("pixelHeight:"):
                    h = int(line.split(":", 1)[1].strip())
            if w and h:
                return (w, h)
    except Exception:
        pass
    return None


def walk_media(root: Path, max_depth: int):
    """Yield (Path, depth) for each media file under root, capped at max_depth."""
    if not root.exists():
        return
    root = root.resolve()
    base_depth = len(root.parts)
    for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
        depth = len(Path(dirpath).parts) - base_depth
        if depth >= max_depth:
            dirnames[:] = []
            continue
        # prune
        dirnames[:] = [
            d for d in dirnames
            if d not in SKIP_DIR_NAMES
            and not any(d.endswith(suf) for suf in SKIP_BUNDLE_SUFFIXES)
            and not d.startswith(".")
        ]
        for fn in filenames:
            if fn.startswith(".") or fn.startswith("._"):
                continue
            p = Path(dirpath) / fn
            ext = p.suffix.lower()
            if ext in ALL_MEDIA:
                yield p, depth


def main():
    print(f"[1/3] Walking {len(ROOTS)} roots (max depth={MAX_DEPTH})...")
    records = []
    t0 = time.time()
    for root in ROOTS:
        print(f"      scanning: {root}")
        for path, depth in walk_media(root, MAX_DEPTH):
            try:
                st = path.stat()
            except OSError:
                continue
            ext = path.suffix.lower()
            cls = media_class(ext)
            rec: dict = {
                "path": str(path),
                "name": path.name,
                "ext": ext,
                "class": cls,
                "size_bytes": st.st_size,
                "size_mb": round(st.st_size / 1024 / 1024, 2),
                "mtime": int(st.st_mtime),
                "mtime_iso": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(st.st_mtime)),
                "depth": depth,
                "root": str(root) if str(path).startswith(str(root)) else "?",
            }
            records.append(rec)
    print(f"      found {len(records)} media files in {time.time()-t0:.1f}s")

    print("[2/3] Probing duration/dimensions (ffprobe + sips)...")
    probed = 0
    t1 = time.time()
    # Limit probe pass to keep wall-time bounded — only probe top-1000 most recent
    probe_targets = sorted(records, key=lambda r: r["mtime"], reverse=True)[:1000]
    for rec in probe_targets:
        p = Path(rec["path"])
        if rec["class"] in ("video", "audio"):
            dur = probe_duration(p)
            if dur is not None:
                rec["duration_s"] = dur
        elif rec["class"] == "image":
            dim = probe_image_dimensions(p)
            if dim:
                rec["width"], rec["height"] = dim
                rec["aspect"] = round(dim[0] / dim[1], 3)
        probed += 1
    print(f"      probed {probed} files in {time.time()-t1:.1f}s")

    out_path = Path("/tmp/helen_media_inventory_v1.json")
    print(f"[3/3] Writing manifest → {out_path}")
    out_path.write_text(json.dumps({
        "version": 1,
        "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "roots": [str(r) for r in ROOTS],
        "max_depth": MAX_DEPTH,
        "total_records": len(records),
        "records": records,
    }, indent=2))
    print(f"      wrote {len(records)} records, {out_path.stat().st_size/1024:.0f} KB")

    # Summary
    print()
    print("=== HELEN MEDIA INVENTORY v1 — SUMMARY ===")
    by_class: dict[str, dict] = {}
    for rec in records:
        c = rec["class"]
        by_class.setdefault(c, {"count": 0, "total_mb": 0.0})
        by_class[c]["count"] += 1
        by_class[c]["total_mb"] += rec["size_mb"]
    for c in ("video", "audio", "image"):
        s = by_class.get(c, {"count": 0, "total_mb": 0.0})
        print(f"  {c:6s}: {s['count']:5d} files · {s['total_mb']:9.1f} MB")

    by_root: dict[str, int] = {}
    for rec in records:
        by_root[rec["root"]] = by_root.get(rec["root"], 0) + 1
    print()
    print("by root:")
    for r, n in sorted(by_root.items(), key=lambda kv: -kv[1]):
        print(f"  {n:5d}  {r}")

    print()
    print("top 10 largest:")
    for rec in sorted(records, key=lambda r: r["size_mb"], reverse=True)[:10]:
        print(f"  {rec['size_mb']:8.1f} MB  {rec['class']:5s}  {rec['name']}")

    print()
    print("top 10 most recent:")
    for rec in sorted(records, key=lambda r: r["mtime"], reverse=True)[:10]:
        print(f"  {rec['mtime_iso']}  {rec['class']:5s}  {rec['name']}")

    print()
    print(f"manifest: {out_path}")


if __name__ == "__main__":
    main()
