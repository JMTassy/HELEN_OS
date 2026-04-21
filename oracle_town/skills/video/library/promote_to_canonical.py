"""promote_to_canonical — copy + rename stills into refs/canonical/ with
canonical names per taxonomy.md.

Non-destructive: originals stay in place. Converts jpg/jpeg → png via PIL
for canonical lossless storage. Updates canonical_manifest.json with source
provenance.

Usage:
    python3 promote_to_canonical.py --plan plan.json [--dest DIR] [--dry-run]

Plan format (list of rename operations):
    [
      {"src": "/absolute/path/orig.jpg", "canonical": "helen_emotions_joy_00.png",
       "theme": "emotions", "descriptor": "joy", "provenance": "operator_desktop"},
      ...
    ]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
import time
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    print("ERROR: Pillow required.", file=sys.stderr)
    sys.exit(3)


def sha256_short(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()[:16]


def promote_one(src: Path, dest_dir: Path, canonical_name: str, dry_run: bool) -> dict:
    dest_path = dest_dir / canonical_name
    if src.suffix.lower() in (".jpg", ".jpeg") and canonical_name.endswith(".png"):
        action = "convert_jpg_to_png"
    elif src.suffix.lower() == ".png" and canonical_name.endswith(".png"):
        action = "copy_png"
    else:
        action = "direct_copy"
    info = {
        "src": str(src),
        "dest": str(dest_path),
        "action": action,
        "src_sha16": sha256_short(src),
        "src_size_bytes": src.stat().st_size,
    }
    if dry_run:
        info["dry_run"] = True
        return info
    dest_dir.mkdir(parents=True, exist_ok=True)
    if action == "convert_jpg_to_png":
        img = Image.open(src).convert("RGB")
        img.save(dest_path, "PNG")
    else:
        shutil.copy2(src, dest_path)
    info["dest_sha16"] = sha256_short(dest_path)
    info["dest_size_bytes"] = dest_path.stat().st_size
    return info


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan", required=True, help="JSON list of rename ops")
    ap.add_argument("--dest", default="helen_os/render/math_to_face_starter/refs/canonical",
                    help="destination root")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    plan = json.loads(Path(args.plan).read_text())
    dest_root = Path(args.dest)

    results: list[dict] = []
    for op in plan:
        theme = op["theme"]
        canonical = op["canonical"]
        src = Path(op["src"])
        if not src.exists():
            results.append({"src": str(src), "status": "src_not_found"})
            continue
        dest_dir = dest_root / theme
        info = promote_one(src, dest_dir, canonical, args.dry_run)
        info["theme"] = theme
        info["descriptor"] = op.get("descriptor")
        info["provenance"] = op.get("provenance", "unspecified")
        results.append(info)
        mark = "[dry-run] " if args.dry_run else ""
        print(f"  {mark}{info['action']:22s}  {src.name:40s} → {theme}/{canonical}")

    if not args.dry_run:
        manifest_path = dest_root / "canonical_manifest.json"
        manifest: dict = {}
        if manifest_path.exists():
            manifest = json.loads(manifest_path.read_text())
        existing = manifest.get("assets", [])
        existing_names = {a["canonical"] for a in existing}
        for r in results:
            if r.get("status") == "src_not_found":
                continue
            canonical = Path(r["dest"]).name
            if canonical in existing_names:
                continue
            existing.append({
                "canonical": canonical,
                "theme": r["theme"],
                "descriptor": r.get("descriptor"),
                "provenance": r["provenance"],
                "src_sha16": r["src_sha16"],
                "dest_sha16": r.get("dest_sha16"),
                "promoted_at_unix": int(time.time()),
            })
        manifest = {
            "schema": "canonical_manifest_v1",
            "dest_root": str(dest_root),
            "n_assets": len(existing),
            "assets": sorted(existing, key=lambda a: (a["theme"], a["canonical"])),
        }
        manifest_path.write_text(json.dumps(manifest, indent=2))
        print(f"\n[promote] manifest: {manifest_path}  (n_assets={manifest['n_assets']})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
