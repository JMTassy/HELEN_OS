"""
HELEN Render — HTML → MP4 renderer.

Two modes:
  stub:        hash-only, no subprocess (tests, CI)
  hyperframes: npx hyperframes render (local, requires node + ffmpeg)

Renderer is commodity. Director plan is the creative decision.
This module only transforms structured data into bytes.
No reasoning. No authority.

Real call:
  npx hyperframes render \\
    --input  {comp_html_path} \\
    --output {output_path}    \\
    --width  1920 --height 1080 --fps 30 \\
    --duration {duration}
"""
from __future__ import annotations

import json
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Literal

from .composition import HTMLCompositionV1
from .contracts import canonical_json, sha256_hex

RenderMode = Literal["stub", "hyperframes"]

_THIS_DIR        = Path(__file__).parent
RENDERER_JS      = Path(os.getenv(
    "HELEN_RENDERER_JS",
    str(_THIS_DIR.parent.parent / "oracle_town/skills/video/hyperframes/renderer.js"),
))
OUTPUT_DIR       = Path("artifacts/render")


def render_composition(
    comp: HTMLCompositionV1,
    mode: RenderMode = "stub",
    output_dir: Path = OUTPUT_DIR,
) -> dict:
    """
    HTMLCompositionV1 → render result dict.

    Returns:
        {
            "mime_type":    "video/mp4",
            "content_hash": "sha256:...",
            "path":         "artifacts/render/....mp4",
            "duration":     N,
            "metadata":     {...},
        }
    """
    if mode == "stub":
        return _render_stub(comp)
    elif mode == "hyperframes":
        return _render_hyperframes(comp, output_dir)
    else:
        raise ValueError(f"Unknown render mode: {mode}")


# ── Stub renderer ──────────────────────────────────────────────────────────────

def _render_stub(comp: HTMLCompositionV1) -> dict:
    output_hash = sha256_hex(comp.html + canonical_json([a.src for a in comp.assets]))
    return {
        "mime_type":    "video/mp4",
        "content_hash": "sha256:" + output_hash,
        "path":         f"artifacts/render/{output_hash[:16]}.mp4",
        "duration":     comp.duration,
        "metadata": {
            "stub":           True,
            "composition_id": comp.composition_id,
            "shots":          comp.html.count('class="shot '),
            "width":          comp.width,
            "height":         comp.height,
            "fps":            comp.fps,
        },
    }


# ── HyperFrames renderer ───────────────────────────────────────────────────────

def _render_hyperframes(comp: HTMLCompositionV1, output_dir: Path) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)
    output_name = f"{comp.composition_id}.mp4"
    output_path = output_dir / output_name

    with tempfile.NamedTemporaryFile(suffix=".html", mode="w",
                                     encoding="utf-8", delete=False) as f:
        f.write(comp.html)
        html_path = f.name

    try:
        cmd = [
            "node", str(RENDERER_JS),
            "--input",    html_path,
            "--output",   str(output_path),
            "--width",    str(comp.width),
            "--height",   str(comp.height),
            "--fps",      str(comp.fps),
            "--duration", str(comp.duration),
        ]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=600,
        )
        if result.returncode != 0:
            raise RuntimeError(
                f"HELEN renderer failed:\n{result.stderr}\n{result.stdout}"
            )

        # Parse the JSON receipt from stdout
        import json as _json
        receipt_line = next(
            (l for l in result.stdout.splitlines() if l.strip().startswith("{")),
            None,
        )
        if receipt_line:
            receipt_data = _json.loads(receipt_line)
            file_hash = receipt_data.get("hash", "sha256:unknown")

        return {
            "mime_type":    "video/mp4",
            "content_hash": file_hash,
            "path":         str(output_path),
            "duration":     comp.duration,
            "metadata": {
                "stub":           False,
                "composition_id": comp.composition_id,
                "renderer":       "hyperframes",
                "width":          comp.width,
                "height":         comp.height,
                "fps":            comp.fps,
            },
        }
    finally:
        Path(html_path).unlink(missing_ok=True)


# ── Manifest writer ────────────────────────────────────────────────────────────

def write_composition_manifest(
    comp:   HTMLCompositionV1,
    result: dict,
    output_dir: Path = OUTPUT_DIR,
) -> Path:
    """Write a provenance JSON alongside the video."""
    manifest = {
        "composition_id":      comp.composition_id,
        "source_artifact_id":  comp.source_artifact_id,
        "source_receipt_hash": comp.source_receipt_hash,
        "plan_id":             comp.plan_id,
        "plan_hash":           comp.plan_hash,
        "composition_hash":    comp.composition_hash,
        "output_hash":         result["content_hash"],
        "output_path":         result["path"],
        "duration":            result["duration"],
        "authority":           False,
    }
    manifest_path = output_dir / f"{comp.composition_id}.provenance.json"
    manifest_path.write_text(json.dumps(manifest, indent=2))
    return manifest_path
