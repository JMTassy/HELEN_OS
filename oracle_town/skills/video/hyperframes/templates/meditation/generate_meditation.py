#!/usr/bin/env python3
"""
generate_meditation.py — HELEN TEMPLE HER video generator.

Reads meditation.config.json, injects values into composition HTML templates,
calls HELEN OS voice engine for voiceover, then renders via npx hyperframes.

Usage:
    python3 generate_meditation.py                    # uses meditation.config.json
    python3 generate_meditation.py --config my.json   # custom config
    python3 generate_meditation.py --preview          # open studio, don't render
    python3 generate_meditation.py --dry-run          # inject + TTS, skip render

Law: authority=NONE. This script never promotes claims. It renders sealed work.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE        = Path(__file__).parent
REPO_ROOT   = HERE.parents[5]          # helen_os_v1/
ARTIFACTS   = REPO_ROOT / "artifacts"
AUDIO_DIR   = ARTIFACTS / "audio"
MEDIA_DIR   = ARTIFACTS / "media"
CONFIG_PATH = HERE / "meditation.config.json"
TTS_SCRIPT  = REPO_ROOT / "oracle_town/skills/voice/gemini_tts/helen_tts.py"

COMPOSITIONS = [
    HERE / "compositions" / "01-sigil.html",
    HERE / "compositions" / "02-temple-breath.html",
    HERE / "compositions" / "03-text-river.html",
    HERE / "compositions" / "04-receipt-seal.html",
]


# ── Helpers ───────────────────────────────────────────────────────────────────

def sha256_file(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_config(path: Path) -> dict:
    raw = json.loads(path.read_text())
    missing = [k for k in ("date", "meditation_text", "run_hash", "commit_sha")
               if "{{" in raw.get(k, "{{")]
    if missing:
        print(f"[WARN] Unfilled placeholders in config: {missing}")
    return raw


def inject_html(src: Path, dest: Path, cfg: dict) -> None:
    """Replace {{PLACEHOLDER}} tokens and inject window vars into a composition."""
    html = src.read_text()

    # Simple token replacement
    replacements = {
        "{{DATE}}":        cfg.get("date", now_iso()[:10]),
        "{{MEDITATION_TEXT}}": cfg.get("meditation_text", ""),
        "{{RUN_HASH}}":    cfg.get("run_hash", ""),
        "{{COMMIT_SHA}}":  cfg.get("commit_sha", ""),
        "{{COMMIT_REPO}}": cfg.get("commit_repo", ""),
    }
    for token, value in replacements.items():
        html = html.replace(token, value)

    # Also inject as window vars before </body> for JS access
    js_inject = f"""
  <script>
    window.__MEDITATION_TEXT__ = {json.dumps(cfg.get('meditation_text', ''))};
    window.__RUN_HASH__        = {json.dumps(cfg.get('run_hash', ''))};
    window.__COMMIT_SHA__      = {json.dumps(cfg.get('commit_sha', ''))};
    window.__COMMIT_REPO__     = {json.dumps(cfg.get('commit_repo', ''))};
  </script>
"""
    html = html.replace("</body>", js_inject + "</body>")
    dest.write_text(html)


def generate_voiceover(text: str, output_path: Path) -> Path | None:
    """Call HELEN OS voice engine to generate voiceover WAV."""
    if not TTS_SCRIPT.exists():
        print(f"[WARN] TTS script not found at {TTS_SCRIPT} — skipping voiceover")
        return None
    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        print("[WARN] No GEMINI_API_KEY/GOOGLE_API_KEY — skipping voiceover")
        return None

    output_path.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        sys.executable, str(TTS_SCRIPT),
        text,
        "--voice", "Zephyr",
        "--output", str(output_path),
    ]
    print(f"[TTS] Generating voiceover → {output_path.name}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"[ERROR] TTS failed:\n{result.stderr}")
        return None
    print(f"[TTS] OK — {output_path.stat().st_size // 1024}KB")
    return output_path


def write_provenance(render_path: Path, cfg: dict, composition_shas: dict,
                     vo_path: Path | None) -> Path:
    """Write provenance.json alongside the rendered MP4."""
    prov = {
        "rendered_at": now_iso(),
        "authority": "NONE",
        "non_sovereign": True,
        "topic": cfg.get("topic", ""),
        "date": cfg.get("date", ""),
        "run_hash": cfg.get("run_hash", ""),
        "commit_sha": cfg.get("commit_sha", ""),
        "commit_repo": cfg.get("commit_repo", ""),
        "composition_shas": composition_shas,
        "voiceover_sha": sha256_file(vo_path) if vo_path and vo_path.exists() else None,
        "render_sha": sha256_file(render_path) if render_path.exists() else None,
        "meditation_text_sha": "sha256:" + hashlib.sha256(
            cfg.get("meditation_text", "").encode()
        ).hexdigest(),
    }
    prov_path = render_path.with_suffix(".provenance.json")
    prov_path.write_text(json.dumps(prov, indent=2))
    return prov_path


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(description="HELEN TEMPLE HER meditation generator")
    parser.add_argument("--config",   default=str(CONFIG_PATH), help="Path to meditation.config.json")
    parser.add_argument("--preview",  action="store_true",      help="Open HyperFrames studio, don't render")
    parser.add_argument("--dry-run",  action="store_true",      help="Inject + TTS only, skip npx render")
    parser.add_argument("--output",   default=None,             help="Override output MP4 path")
    args = parser.parse_args()

    cfg = load_config(Path(args.config))
    date_slug = cfg.get("date", now_iso()[:10]).replace("-", "")
    topic_slug = re.sub(r"[^a-z0-9]+", "_", cfg.get("topic", "meditation").lower())[:30]

    # ── Build dir: copy templates into a working build ──────────────────────
    build_dir = HERE / "_build"
    if build_dir.exists():
        shutil.rmtree(build_dir)
    shutil.copytree(HERE, build_dir, ignore=shutil.ignore_patterns("_build", "*.py", "*.json"))

    # Inject config into all compositions + index
    composition_shas = {}
    for src in [HERE / "index.html"] + COMPOSITIONS:
        dest = build_dir / src.relative_to(HERE)
        dest.parent.mkdir(parents=True, exist_ok=True)
        inject_html(src, dest, cfg)
        composition_shas[src.name] = sha256_file(dest)
        print(f"[INJ] {src.name}")

    # ── Voiceover ────────────────────────────────────────────────────────────
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    vo_filename = f"{date_slug}__{topic_slug}.wav"
    vo_path = AUDIO_DIR / vo_filename
    assets_dir = build_dir / "assets"
    assets_dir.mkdir(exist_ok=True)

    if not vo_path.exists():
        generate_voiceover(cfg["meditation_text"], vo_path)
    else:
        print(f"[TTS] Reusing existing {vo_filename}")

    # Copy voiceover into build assets
    if vo_path.exists():
        shutil.copy(vo_path, assets_dir / "voiceover.wav")

    # ── Render ───────────────────────────────────────────────────────────────
    MEDIA_DIR.mkdir(parents=True, exist_ok=True)
    output_path = Path(args.output) if args.output else \
                  MEDIA_DIR / f"{date_slug}__{topic_slug}.mp4"

    if args.preview:
        print(f"[PREVIEW] Opening studio at {build_dir}")
        subprocess.run(["npx", "hyperframes", "preview"], cwd=build_dir)
        return 0

    if args.dry_run:
        print(f"[DRY-RUN] Build ready at {build_dir}. Skipping render.")
        return 0

    print(f"[RENDER] {build_dir} → {output_path}")
    result = subprocess.run(
        ["npx", "hyperframes", "render", "--output", str(output_path)],
        cwd=build_dir,
    )
    if result.returncode != 0:
        print("[ERROR] npx hyperframes render failed")
        return 1

    # ── Provenance ───────────────────────────────────────────────────────────
    prov_path = write_provenance(output_path, cfg, composition_shas, vo_path)
    render_sha = sha256_file(output_path) if output_path.exists() else "—"

    print(f"\n── HELEN TEMPLE MEDITATION — SEALED ──────────────────")
    print(f"  output:     {output_path}")
    print(f"  render_sha: {render_sha[:40]}...")
    print(f"  provenance: {prov_path.name}")
    print(f"  authority:  NONE")
    print(f"  receipt:    {cfg.get('run_hash','')[:40]}...")
    print(f"──────────────────────────────────────────────────────")
    return 0


if __name__ == "__main__":
    sys.exit(main())
