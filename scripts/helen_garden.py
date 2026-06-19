#!/usr/bin/env python3
"""
helen_garden.py — render a knowledge directory as an ASCII GARDEN.

STATUS: NON_SOVEREIGN · NO_CLAIM · authority=false
A read-only diagnostic surface. It walks a knowledge tree (default
helen_os/knowledge/) and prints each folder as a garden "bed", with a
bloom-density bar and advisory health flags (missing README, empty, dense,
stale corpus, orphan files, reading-path presence).

It writes nothing. It never touches the ledger, kernel, schemas, receipts,
seals, or sovereign memory. The verdict (if any) belongs to the gates, not
to this tool — every row is backed by a real os.scandir read, and absence is
rendered explicitly rather than faked.

Design mirrors oracle_town/city_state_renderer.py:
  * scan_garden()  does ALL I/O and returns a plain dict
  * render_garden() is PURE — no I/O, no time, no randomness → deterministic

Usage:
  python3 scripts/helen_garden.py [--root helen_os/knowledge] [--depth 2] [--no-color]
"""
from __future__ import annotations

import argparse
import os
import sys
from typing import Dict, List, Optional

# ─────────────────────────────────────────────────────────────────────
# Canonical constants (frozen)
# ─────────────────────────────────────────────────────────────────────

BAR_WIDTH = 5
DENSE_THRESHOLD = 1000          # a bed with more files than this is a "forest"
SKIP_DIRS = {"__pycache__"}
SKIP_SUFFIX = (".pyc",)
README_NAMES = {"readme.md", "readme", "readme.txt"}
INDEX_HINTS = {"corpus.json"}   # files whose staleness we check

GLYPH_FULL = "█"
GLYPH_EMPTY = "░"

# Emoji vs plain tokens (--no-color swaps to the right column)
TOKENS = {
    "warn":    ("⚠", "!"),
    "forest":  ("🌲", "#"),
    "horse":   ("🐎", "horse"),
    "crown":   ("👑🚫", "no-god"),
    "garden":  ("🌿", "*"),
}


# ─────────────────────────────────────────────────────────────────────
# Scan layer (does I/O) — returns a plain, render-ready dict
# ─────────────────────────────────────────────────────────────────────

def _is_real_file(entry: os.DirEntry) -> bool:
    name = entry.name
    if name.startswith("."):
        return False
    if name.endswith(SKIP_SUFFIX):
        return False
    return entry.is_file()


def _has_readme(dir_path: str) -> bool:
    try:
        for entry in os.scandir(dir_path):
            if entry.is_file() and entry.name.lower() in README_NAMES:
                return True
    except OSError:
        return False
    return False


def _newest_md_mtime(dir_path: str) -> float:
    """Newest .md mtime anywhere under dir_path (for staleness check)."""
    newest = 0.0
    for cur, dirs, files in os.walk(dir_path):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not d.startswith(".")]
        for f in files:
            if f.endswith(".md"):
                try:
                    m = os.stat(os.path.join(cur, f)).st_mtime
                    if m > newest:
                        newest = m
                except OSError:
                    continue
    return newest


def _scan_bed(dir_path: str, name: str, depth: int, max_depth: int) -> Dict:
    """Recursively scan one bed. file_count is non-recursive (direct files)."""
    file_count = 0
    subdirs: List[os.DirEntry] = []
    try:
        for entry in os.scandir(dir_path):
            if entry.name in SKIP_DIRS or entry.name.startswith("."):
                continue
            if _is_real_file(entry):
                file_count += 1
            elif entry.is_dir():
                subdirs.append(entry)
    except OSError:
        pass

    subdirs.sort(key=lambda e: e.name)
    is_dense = file_count > DENSE_THRESHOLD
    flags: List[str] = []
    if file_count == 0 and not subdirs:
        flags.append("empty")
    if not _has_readme(dir_path):
        flags.append("no_readme")
    if is_dense:
        flags.append("dense")

    children: List[Dict] = []
    # Do not descend into a dense forest (avoids O(27k) enumeration) and
    # respect the depth cap.
    if depth < max_depth and not is_dense:
        for sub in subdirs:
            children.append(_scan_bed(sub.path, sub.name, depth + 1, max_depth))

    return {
        "name": name,
        "depth": depth,
        "file_count": file_count,
        "subdir_count": len(subdirs),
        "is_dense": is_dense,
        "flags": sorted(flags),
        "children": children,
    }


def _flatten(beds: List[Dict]) -> List[Dict]:
    out: List[Dict] = []
    for b in beds:
        out.append(b)
        out.extend(_flatten(b["children"]))
    return out


def scan_garden(root: str, max_depth: int = 2) -> Dict:
    """Walk `root` and return a plain dict ready for pure rendering."""
    state: Dict = {
        "root": root,
        "exists": os.path.isdir(root),
        "beds": [],
        "orphans": [],
        "reading_path": False,
        "stale_corpus": None,
        "max_count": 0,
    }
    if not state["exists"]:
        return state

    top_dirs: List[os.DirEntry] = []
    orphans: List[str] = []
    try:
        for entry in os.scandir(root):
            if entry.name in SKIP_DIRS or entry.name.startswith("."):
                continue
            if entry.is_dir():
                top_dirs.append(entry)
            elif _is_real_file(entry):
                orphans.append(entry.name)
    except OSError:
        pass

    top_dirs.sort(key=lambda e: e.name)
    orphans.sort()

    beds = [_scan_bed(d.path, d.name, 1, max_depth) for d in top_dirs]
    flat = _flatten(beds)
    # Scale the density bars among NON-dense beds only, so one forest
    # (e.g. embeddings ~27k) does not flatten every real bed to a single cell.
    max_count = max((b["file_count"] for b in flat if not b["is_dense"]), default=0)

    # reading-path presence (rendered honestly, never faked)
    names = {b["name"].lower() for b in beds} | {o.lower() for o in orphans}
    reading_path = any(
        n in names for n in ("reading-path", "reading_path", "map", "map.md")
    )

    # corpus staleness: index file older than newest source .md
    stale: Optional[bool] = None
    for hint in INDEX_HINTS:
        hint_path = os.path.join(root, hint)
        if os.path.isfile(hint_path):
            try:
                idx_mtime = os.stat(hint_path).st_mtime
                newest_md = _newest_md_mtime(root)
                stale = newest_md > idx_mtime if newest_md else False
            except OSError:
                stale = None
            break

    state.update({
        "beds": beds,
        "orphans": orphans,
        "reading_path": reading_path,
        "stale_corpus": stale,
        "max_count": max_count,
    })
    return state


# ─────────────────────────────────────────────────────────────────────
# Render layer (PURE — no I/O, no time, no randomness)
# ─────────────────────────────────────────────────────────────────────

def _bar(count: int, max_count: int) -> str:
    """Density bar scaled to BAR_WIDTH relative to the busiest bed."""
    if max_count <= 0:
        filled = 0
    else:
        filled = round(BAR_WIDTH * count / max_count)
        if count > 0:
            filled = max(1, filled)
        filled = min(BAR_WIDTH, filled)
    return GLYPH_FULL * filled + GLYPH_EMPTY * (BAR_WIDTH - filled)


def _tok(key: str, color: bool) -> str:
    emoji, plain = TOKENS[key]
    return emoji if color else plain


def _flag_text(bed: Dict, color: bool) -> str:
    warn = _tok("warn", color)
    parts: List[str] = []
    flags = set(bed["flags"])
    if "no_readme" in flags:
        parts.append(f"{warn} no README")
    if "empty" in flags:
        parts.append(f"{warn} empty")
    if bed["is_dense"]:
        parts.append(f"{_tok('forest', color)} dense forest "
                     f"({bed['file_count']}, summarized)")
    return "   " + "   ".join(parts) if parts else ""


def _render_bed_lines(bed: Dict, max_count: int, color: bool) -> List[str]:
    indent = "  " * bed["depth"]
    name = bed["name"] + "/"
    if bed["is_dense"]:
        bar = GLYPH_FULL * BAR_WIDTH
        seeds = ""
    else:
        bar = _bar(bed["file_count"], max_count)
        seeds = f"{bed['file_count']:>3} seeds"
    label = f"{indent}{name:<18}".rstrip()
    label = f"{indent}{name:<18}"
    line = f"  {label} {bar}  {seeds}{_flag_text(bed, color)}".rstrip()
    lines = [line]
    for child in bed["children"]:
        lines.extend(_render_bed_lines(child, max_count, color))
    return lines


def render_garden(state: Dict, color: bool = True) -> str:
    """Pure render: same state dict → byte-identical output."""
    garden = _tok("garden", color)
    horse = _tok("horse", color)
    crown = _tok("crown", color)
    warn = _tok("warn", color)

    root = state["root"]
    lines: List[str] = []
    lines.append(f"╔══ {garden} HELEN GARDEN · {root} ".ljust(62, "═") + " NO_CLAIM ══╗")

    if not state["exists"]:
        lines.append(f"  {warn} no garden here — root does not exist: {root}")
        lines.append("╚" + "═" * 62 + "╝")
        return "\n".join(lines)

    beds = state["beds"]
    if not beds:
        lines.append("  (no beds — root has no sub-directories)")
    flat = _flatten(beds)
    for bed in beds:
        lines.extend(_render_bed_lines(bed, state["max_count"], color))

    lines.append("  " + "─" * 60)

    rp = "present" if state["reading_path"] else "(none)"
    lines.append(f"  reading-path:      {rp}")

    if state["orphans"]:
        lines.append("  ORPHANS:           " + " · ".join(state["orphans"]))

    if state["stale_corpus"] is True:
        lines.append(f"  corpus.json:       {warn} stale "
                     f"(older than newest source .md)")
    elif state["stale_corpus"] is False:
        lines.append("  corpus.json:       fresh")

    lines.append("  " + "─" * 60)

    n_beds = len(flat)
    n_noreadme = sum(1 for b in flat if "no_readme" in b["flags"])
    n_dense = sum(1 for b in flat if b["is_dense"])
    n_empty = sum(1 for b in flat if "empty" in b["flags"])
    n_orphans = len(state["orphans"])
    summary = (f"HEALTH: {n_beds} beds · {n_noreadme} {warn} no-README · "
               f"{n_dense} dense · {n_empty} empty · {n_orphans} orphans")
    lines.append("  " + summary)

    footer = f" {horse} all surface · replayable · {crown} "
    lines.append("╚" + footer.center(62, "═") + "╝")
    return "\n".join(lines)


# ─────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────

def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Render a knowledge directory as an ASCII GARDEN "
                    "(read-only, NO_CLAIM).")
    parser.add_argument("--root", default="helen_os/knowledge",
                        help="knowledge root to render (default: helen_os/knowledge)")
    parser.add_argument("--depth", type=int, default=2,
                        help="max bed recursion depth (default: 2)")
    parser.add_argument("--no-color", action="store_true",
                        help="plain ASCII tokens instead of emoji glyphs")
    args = parser.parse_args(argv)

    state = scan_garden(args.root, max_depth=max(1, args.depth))
    print(render_garden(state, color=not args.no_color))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
