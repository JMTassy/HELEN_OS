#!/usr/bin/env python3
"""
HELEN heuristic filter v1 — pattern-based candidate selection from media inventory.

Reads:  /tmp/helen_media_inventory_v1.json (output of helen_media_inventory_v1.py)
Writes: /tmp/helen_canon_candidates_v1.json

Zero API calls. Zero spend. Pure regex + path heuristics.

Categorizes each media file by HELEN-relevance patterns. A file may match multiple
categories (score = number of matches). Candidates are sorted by score desc, then
mtime desc.

Non-sovereign tool. Does NOT promote any media to canon, does NOT write to ledger,
does NOT classify content (only filenames/paths).
"""
import json
import re
import time
from pathlib import Path

INPUT = Path("/tmp/helen_media_inventory_v1.json")
OUTPUT = Path("/tmp/helen_canon_candidates_v1.json")

# ── Categories with case-insensitive patterns ────────────────────────────────
# Patterns match against file path (which includes filename and parent dirs).
CATEGORIES = {
    "HELEN_CHARACTER": [
        r"\bhelen\b",          # word "helen"
        r"HELEN_AVATAR",       # operator's avatar dir
        r"HELEN_OS_PICS",      # operator's HELEN images dir
        r"\bhf_2026",          # Higgsfield-generated outputs (hf_YYYYMMDD pattern)
        r"\bavatar\b",
        r"\bportrait\b",
        r"copper.?red",        # canonical hair color
    ],
    "HELEN_SCENE": [
        r"\btemple\b",
        r"\binitiation\b",
        r"\bUNRIPPLE\b",
        r"\bcourtyard\b",
        r"\bmystery\b",
        r"\bsanctum\b",
        r"\bpyramid\b",        # canonical era
    ],
    "AI_VIDEO_NAMED": [
        r"\bc1091\b",
        r"\bfilmr\b",
        r"\brose_avatar\b",
        r"\bjm_avatar\b",
        r"\brender\b",
        r"\bseedance\b",
        r"\bkling\b",
        r"\bhiggsfield\b",
        r"\bsoul\b",
    ],
    "RECENT_WORKING": [
        # Recent 3-day operator working artifacts (screenshots, exports)
        r"2026-04-2[6-8]",
        r"\bCapture d.+cran\b",  # macOS French screenshot prefix
    ],
    "AI_GENERATED_IMAGE_UUID": [
        # UUID v4-shaped filenames (typical of API-dropped images)
        r"\b[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}\b",
    ],
    "HELEN_CONQUEST": [
        # CONQUEST visual / world-building assets
        r"\bCONQUEST\b",
        r"\bconquest\b",
        r"\boracle.?town\b",
    ],
    "VOICE_AUDIO": [
        # Audio worth Whisper-transcribing
        r"\b(zephyr|tts|voice|narration|interview|meeting|fireflies)\b",
    ],
}

# Compile all patterns once (case-insensitive)
COMPILED: dict[str, list[re.Pattern]] = {
    cat: [re.compile(p, re.IGNORECASE) for p in pats] for cat, pats in CATEGORIES.items()
}


def categorize(path_str: str) -> list[str]:
    """Return list of categories matching this path."""
    matched = []
    for cat, patterns in COMPILED.items():
        if any(p.search(path_str) for p in patterns):
            matched.append(cat)
    return matched


def main():
    print(f"[1/4] Loading manifest: {INPUT}")
    if not INPUT.exists():
        raise SystemExit(f"FAIL: manifest missing — run tools/helen_media_inventory_v1.py first")
    data = json.loads(INPUT.read_text())
    records = data.get("records", [])
    print(f"      loaded {len(records)} records")

    print("[2/4] Applying heuristic categorization...")
    candidates = []
    cat_counts: dict[str, int] = {c: 0 for c in CATEGORIES}
    for rec in records:
        cats = categorize(rec["path"])
        if not cats:
            continue
        for c in cats:
            cat_counts[c] = cat_counts.get(c, 0) + 1
        candidates.append({
            **{k: rec[k] for k in ("path", "name", "ext", "class", "size_mb", "mtime", "mtime_iso", "root")},
            **{k: rec[k] for k in ("duration_s", "width", "height", "aspect") if k in rec},
            "categories": cats,
            "score": len(cats),
        })
    print(f"      matched {len(candidates)} of {len(records)} ({100*len(candidates)/max(1,len(records)):.1f}%)")

    print("[3/4] Sorting (score desc, mtime desc)...")
    candidates.sort(key=lambda c: (-c["score"], -c["mtime"]))

    print(f"[4/4] Writing → {OUTPUT}")
    OUTPUT.write_text(json.dumps({
        "version": 1,
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "source_manifest": str(INPUT),
        "total_input": len(records),
        "total_candidates": len(candidates),
        "by_category": cat_counts,
        "candidates": candidates,
    }, indent=2))
    print(f"      wrote {len(candidates)} candidates, {OUTPUT.stat().st_size/1024:.0f} KB")

    # ── Summary ──────────────────────────────────────────────────────────────
    print()
    print("=== HELEN HEURISTIC FILTER v1 — SUMMARY ===")
    print(f"  input:      {len(records)} files")
    print(f"  candidates: {len(candidates)}")
    print()
    print("by category:")
    for cat in CATEGORIES.keys():
        n = cat_counts.get(cat, 0)
        bar = "█" * min(40, n) if n > 0 else ""
        print(f"  {cat:28s}: {n:5d}  {bar}")

    # Score distribution
    score_dist: dict[int, int] = {}
    for c in candidates:
        score_dist[c["score"]] = score_dist.get(c["score"], 0) + 1
    print()
    print("score distribution (multi-category matches):")
    for score in sorted(score_dist.keys(), reverse=True):
        print(f"  score={score}: {score_dist[score]:5d} files")

    # Top candidates
    print()
    print("top 20 by score (multi-category, then most recent):")
    for cand in candidates[:20]:
        cats_str = "+".join(c.replace("HELEN_", "").replace("_NAMED", "") for c in cand["categories"])
        size = f"{cand['size_mb']:.1f}MB"
        print(f"  s={cand['score']} {cand['mtime_iso']}  {cand['class']:5s}  {size:>9s}  [{cats_str}]  {cand['name']}")

    # Class breakdown of candidates
    print()
    print("candidate breakdown by class:")
    by_class: dict[str, int] = {}
    for c in candidates:
        by_class[c["class"]] = by_class.get(c["class"], 0) + 1
    for cls in ("video", "audio", "image"):
        n = by_class.get(cls, 0)
        print(f"  {cls:6s}: {n:5d}")

    print()
    print(f"manifest: {OUTPUT}")


if __name__ == "__main__":
    main()
