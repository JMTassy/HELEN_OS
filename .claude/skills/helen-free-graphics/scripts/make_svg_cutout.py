#!/usr/bin/env python3
"""Generate free SVG paper cutouts for HELEN garden surfaces.

authority=false · claim=NO_CLAIM · $0 · no network
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Simple silhouette paths — paper-cut readable at small sizes
SHAPES: dict[str, tuple[str, str]] = {
    # name: (viewBox path fill-rule default color)
    "mushroom": (
        "0 0 64 64",
        "M12 28c0-12 10-22 20-22s20 10 20 22c0 2-1 4-3 4H15c-2 0-3-2-3-4zm14 4h8v20h-8z",
        "#5c7a3a",
    ),
    "tower": (
        "0 0 64 64",
        "M20 56V24l6-10h12l6 10v32H20zm8-28h8v8h-8zm0 12h8v8h-8z",
        "#6b5a2e",
    ),
    "lantern": (
        "0 0 64 64",
        "M28 8h8v6h-8zm-6 6h20l4 8v24c0 4-4 8-10 10h-8c-6-2-10-6-10-10V22l4-8zm10 10c-4 0-6 3-6 8s2 8 6 8 6-3 6-8-2-8-6-8z",
        "#c25e28",
    ),
    "bench": (
        "0 0 64 64",
        "M10 34h44v6H10zm4 6h6v14h-6zm30 0h6v14h-6zm-28-10h36v6H16z",
        "#6b5a2e",
    ),
    "leaf": (
        "0 0 64 64",
        "M12 40c8-20 28-28 40-28-4 16-8 28-24 36-10 4-18 2-16-8z",
        "#2e5940",
    ),
    "bug": (
        "0 0 64 64",
        "M20 20c0-6 6-10 12-10s12 4 12 10v8c4 2 6 6 6 10 0 8-8 14-18 14S14 46 14 38c0-4 2-8 6-10v-8zm8 4h8v4h-8z",
        "#8a3a30",
    ),
    "moon": (
        "0 0 64 64",
        "M40 8c-14 4-24 18-20 32 4 12 16 20 28 18-10 6-24 4-32-6C6 38 10 18 26 10c4-2 10-3 14-2z",
        "#b8860b",
    ),
    "scroll": (
        "0 0 64 64",
        "M14 12h28c4 0 8 4 8 8v28c0 2-2 4-4 4H22c-4 0-8-4-8-8V16c0-2 2-4 4-4zm8 12h20v4H22zm0 10h16v4H22z",
        "#efe7d8",
    ),
}


def svg_for(shape: str, color: str | None) -> str:
    if shape not in SHAPES:
        known = ", ".join(sorted(SHAPES))
        raise SystemExit(f"unknown shape {shape!r}. known: {known}")
    view, path, default_color = SHAPES[shape]
    fill = color or default_color
    # cream keyline via dual path: dark stroke under, fill on top feel via stroke
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="{view}" width="128" height="128" role="img" aria-label="{shape} cutout">
  <!-- HELEN free cutout · authority=false · $0 -->
  <rect width="64" height="64" fill="none"/>
  <path d="{path}" fill="{fill}" stroke="#f5efe0" stroke-width="2.5" stroke-linejoin="round"/>
</svg>
"""


def main() -> int:
    p = argparse.ArgumentParser(description="Make a free HELEN SVG paper cutout")
    p.add_argument("--shape", default="", choices=sorted(SHAPES.keys()) + [""])
    p.add_argument("--color", default="", help="Fill hex, e.g. #5c7a3a")
    p.add_argument("--out", default="", help="Output .svg path")
    p.add_argument("--list", action="store_true", help="List shapes and exit")
    args = p.parse_args()

    if args.list:
        for name in sorted(SHAPES):
            print(name)
        return 0

    if not args.shape or not args.out:
        p.error("--shape and --out are required (unless --list)")

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    color = args.color.strip() or None
    out.write_text(svg_for(args.shape, color), encoding="utf-8")
    print(f"SVG_OK {out} shape={args.shape}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
