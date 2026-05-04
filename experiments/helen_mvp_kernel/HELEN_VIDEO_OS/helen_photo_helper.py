"""HELEN photo helper — scans Windows folders for recent images,
copies the chosen one to ~/helen-conquest/helen_ref.png, and runs
the HeyGen->Telegram pipeline.

ADHD-friendly. Zero copy-paste of paths required.

Usage on MRED (WSL2):
    python helen_photo_helper.py
    python helen_photo_helper.py --text "Custom line for HELEN to say"
    python helen_photo_helper.py --auto    # picks newest image, no prompt
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import List, Tuple

REPO_ROOT = Path(__file__).resolve().parents[3]
TARGET_REF = REPO_ROOT / "helen_ref.png"

WINDOWS_HOME = Path("/mnt/c/Users")
DEFAULT_TEXT = "HELEN sees. HELEN proposes. The gate authorizes."

IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp"}
SCAN_SUBDIRS = ["Downloads", "Desktop", "Pictures"]
MAX_AGE_DAYS = 30
MAX_RESULTS = 15


def find_windows_user_dir() -> Path:
    """Locate the Windows user folder under /mnt/c/Users."""
    if not WINDOWS_HOME.exists():
        raise SystemExit(
            f"{WINDOWS_HOME} not found. Are you running this in WSL2?"
        )
    candidates = [
        d for d in WINDOWS_HOME.iterdir()
        if d.is_dir() and not d.name.startswith(".") and d.name not in (
            "Public", "Default", "Default User", "All Users", "desktop.ini"
        )
    ]
    if not candidates:
        raise SystemExit(f"No user folders under {WINDOWS_HOME}")
    if len(candidates) == 1:
        return candidates[0]
    # If multiple, prefer one that has Downloads or Desktop populated
    candidates.sort(
        key=lambda d: (
            -(d / "Downloads").exists(),
            -(d / "Desktop").exists(),
            d.name,
        )
    )
    return candidates[0]


def scan_images(user_dir: Path) -> List[Tuple[Path, float]]:
    """Return [(path, mtime), ...] sorted newest first, filtered by age + ext."""
    cutoff = time.time() - MAX_AGE_DAYS * 86400
    found: List[Tuple[Path, float]] = []
    for sub in SCAN_SUBDIRS:
        d = user_dir / sub
        if not d.exists():
            continue
        try:
            for p in d.iterdir():
                if not p.is_file():
                    continue
                if p.suffix.lower() not in IMAGE_EXTS:
                    continue
                try:
                    mt = p.stat().st_mtime
                except OSError:
                    continue
                if mt >= cutoff:
                    found.append((p, mt))
        except PermissionError:
            continue
    found.sort(key=lambda x: -x[1])
    return found[:MAX_RESULTS]


def human_age(mtime: float) -> str:
    age_s = time.time() - mtime
    if age_s < 60:
        return f"{int(age_s)}s ago"
    if age_s < 3600:
        return f"{int(age_s / 60)}m ago"
    if age_s < 86400:
        return f"{int(age_s / 3600)}h ago"
    return f"{int(age_s / 86400)}d ago"


def human_size(n: int) -> str:
    if n < 1024:
        return f"{n}B"
    if n < 1024 * 1024:
        return f"{n // 1024}KB"
    return f"{n / (1024 * 1024):.1f}MB"


def pick_image(images: List[Tuple[Path, float]], auto: bool) -> Path:
    if not images:
        raise SystemExit(
            "No recent images found in Downloads / Desktop / Pictures.\n"
            "Save a HELEN image to one of those folders, then re-run.\n"
            f"(scan window: last {MAX_AGE_DAYS} days, exts: "
            f"{sorted(IMAGE_EXTS)})"
        )
    if auto:
        chosen = images[0][0]
        print(f"[auto] picking newest: {chosen.name}")
        return chosen
    print(f"\nFound {len(images)} recent images:\n")
    for i, (p, mt) in enumerate(images, 1):
        try:
            size = p.stat().st_size
        except OSError:
            size = 0
        print(f"  {i:>2}. {p.parent.name:<10} {p.name:<40} "
              f"{human_size(size):>7}  {human_age(mt)}")
    print()
    raw = input("Pick a number (or q to quit): ").strip().lower()
    if raw in ("q", "quit", "exit", ""):
        raise SystemExit("Cancelled.")
    try:
        idx = int(raw)
        if not 1 <= idx <= len(images):
            raise ValueError
    except ValueError:
        raise SystemExit(f"Invalid choice: {raw!r}")
    return images[idx - 1][0]


def copy_to_repo(src: Path) -> Path:
    TARGET_REF.parent.mkdir(parents=True, exist_ok=True)
    # If src is png we keep .png; if jpg/jpeg/webp we still write to helen_ref.<ext>
    target = TARGET_REF.with_suffix(src.suffix.lower())
    shutil.copy2(src, target)
    print(f"[copy] {src} -> {target} ({target.stat().st_size} bytes)")
    return target


def run_render(photo_path: Path, text: str) -> int:
    runner = (
        REPO_ROOT
        / "experiments"
        / "helen_mvp_kernel"
        / "HELEN_VIDEO_OS"
        / "backends"
        / "run_heygen_to_telegram.py"
    )
    if not runner.exists():
        raise SystemExit(f"Runner not found: {runner}")
    cmd = [
        sys.executable,
        str(runner),
        "--photo", str(photo_path),
        "--text", text,
    ]
    print(f"\n[run] {' '.join(cmd)}\n")
    return subprocess.call(cmd)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Pick a HELEN photo from Windows folders, render via HeyGen, post to Telegram."
    )
    parser.add_argument(
        "--text",
        default=DEFAULT_TEXT,
        help=f"Text the avatar will speak (default: {DEFAULT_TEXT!r})",
    )
    parser.add_argument(
        "--auto",
        action="store_true",
        help="Skip the picker; use the newest image found.",
    )
    parser.add_argument(
        "--no-render",
        action="store_true",
        help="Just copy the photo; don't trigger the render.",
    )
    args = parser.parse_args()

    user_dir = find_windows_user_dir()
    print(f"[scan] Windows user: {user_dir}")
    images = scan_images(user_dir)
    chosen = pick_image(images, auto=args.auto)
    target = copy_to_repo(chosen)

    if args.no_render:
        print(f"\nDone. Photo at: {target}")
        print("Run the render manually:")
        print(
            f"  python experiments/helen_mvp_kernel/HELEN_VIDEO_OS/backends/"
            f"run_heygen_to_telegram.py --photo {target} --text \"...\""
        )
        return 0

    return run_render(target, args.text)


if __name__ == "__main__":
    raise SystemExit(main())
