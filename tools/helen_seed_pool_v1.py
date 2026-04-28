#!/usr/bin/env python3
"""
HELEN seed pool v1 — clean seed selection from heuristic candidates.

Reads:  /tmp/helen_canon_candidates_v1.json (output of helen_heuristic_filter_v1.py)
Writes: /tmp/helen_seed_pool_v1.json

Removes screenshot noise. Keeps actual seed material:
  - All video class files (193 candidates → likely seed-quality video assets)
  - Image class WHERE: HELEN_CHARACTER or HELEN_SCENE matched AND filename is NOT a screenshot

Excluded:
  - audio class (separate workflow)
  - RECENT_WORKING-only matches (screenshots that just happened to be in HELEN dir)
  - Pure UUID images without other HELEN tags (too noisy for hand selection)

Zero API calls. Zero spend.
"""
import json
import re
import time
from pathlib import Path

INPUT = Path("/tmp/helen_canon_candidates_v1.json")
OUTPUT = Path("/tmp/helen_seed_pool_v1.json")

SCREENSHOT_RE = re.compile(r"Capture d.+cran", re.IGNORECASE)


def is_screenshot(name: str) -> bool:
    return bool(SCREENSHOT_RE.search(name))


def keep(rec: dict) -> tuple[bool, str]:
    """Decide whether to keep this candidate. Returns (keep, reason)."""
    cls = rec.get("class")
    cats = set(rec.get("categories", []))

    if cls == "video":
        return (True, "video_seed_pool")

    if cls == "audio":
        return (False, "audio_excluded")

    if cls == "image":
        if is_screenshot(rec.get("name", "")):
            return (False, "screenshot_excluded")
        # Keep images that have CHARACTER or SCENE tags
        if "HELEN_CHARACTER" in cats or "HELEN_SCENE" in cats:
            return (True, "image_with_helen_tag")
        # Keep AI-named videos as well even though that's a video pattern (some imgs might match)
        if "AI_VIDEO_NAMED" in cats:
            return (True, "ai_named_image")
        # Drop UUID-only or RECENT_WORKING-only images
        return (False, "image_without_helen_tag")

    return (False, "unknown_class")


def main():
    print(f"[1/3] Loading candidates: {INPUT}")
    if not INPUT.exists():
        raise SystemExit("FAIL: candidates manifest missing — run helen_heuristic_filter_v1.py first")
    data = json.loads(INPUT.read_text())
    candidates = data.get("candidates", [])
    print(f"      loaded {len(candidates)} candidates")

    print("[2/3] Filtering to seed pool...")
    pool: list[dict] = []
    drop_reasons: dict[str, int] = {}
    for rec in candidates:
        ok, reason = keep(rec)
        if ok:
            rec_out = dict(rec)
            rec_out["pool_reason"] = reason
            pool.append(rec_out)
        else:
            drop_reasons[reason] = drop_reasons.get(reason, 0) + 1

    # Sort: score desc, then mtime desc, then size desc
    pool.sort(key=lambda r: (-r.get("score", 0), -r.get("mtime", 0), -r.get("size_mb", 0)))

    print(f"      kept {len(pool)} of {len(candidates)} ({100*len(pool)/max(1,len(candidates)):.1f}%)")
    for reason, n in sorted(drop_reasons.items(), key=lambda kv: -kv[1]):
        print(f"      dropped: {n:5d}  [{reason}]")

    print(f"[3/3] Writing → {OUTPUT}")
    OUTPUT.write_text(json.dumps({
        "version": 1,
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "source_candidates": str(INPUT),
        "total_input": len(candidates),
        "total_pool": len(pool),
        "drop_reasons": drop_reasons,
        "pool": pool,
    }, indent=2))
    print(f"      wrote {len(pool)} pool entries, {OUTPUT.stat().st_size/1024:.0f} KB")

    # ── Summary ──────────────────────────────────────────────────────────────
    print()
    print("=== HELEN SEED POOL v1 — SUMMARY ===")
    by_class: dict[str, int] = {}
    by_score: dict[int, int] = {}
    total_size_mb = 0.0
    for r in pool:
        by_class[r["class"]] = by_class.get(r["class"], 0) + 1
        by_score[r.get("score", 0)] = by_score.get(r.get("score", 0), 0) + 1
        total_size_mb += r.get("size_mb", 0)

    print(f"  pool size: {len(pool)} files · {total_size_mb:.0f} MB total")
    print()
    print("by class:")
    for cls in ("video", "image", "audio"):
        n = by_class.get(cls, 0)
        bar = "█" * min(40, n // 5) if n > 0 else ""
        print(f"  {cls:6s}: {n:5d}  {bar}")

    print()
    print("by score:")
    for s in sorted(by_score.keys(), reverse=True):
        print(f"  score={s}: {by_score[s]}")

    print()
    print("top 15 video seeds (score, mtime, size):")
    videos = [r for r in pool if r["class"] == "video"]
    for r in videos[:15]:
        cats = "+".join(c.replace("HELEN_", "").replace("_NAMED", "") for c in r.get("categories", []))
        print(f"  s={r['score']} {r['mtime_iso']}  {r['size_mb']:>7.1f}MB  [{cats:30s}]  {r['name']}")

    print()
    print("top 15 image seeds (HELEN-tagged non-screenshots):")
    images = [r for r in pool if r["class"] == "image"]
    for r in images[:15]:
        cats = "+".join(c.replace("HELEN_", "").replace("_NAMED", "") for c in r.get("categories", []))
        size = f"{r['size_mb']:.1f}MB"
        print(f"  s={r['score']} {r['mtime_iso']}  {size:>9s}  [{cats:30s}]  {r['name']}")

    print()
    print(f"manifest: {OUTPUT}")


if __name__ == "__main__":
    main()
