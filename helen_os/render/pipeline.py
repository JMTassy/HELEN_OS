"""
HELEN Render — pipeline wrapper.

Two render paths:

PATH A — legacy spec (tests, backward compat):
  ExecutionArtifactV1
  → DirectorPlanV1
  → compile_video_spec → dict spec → render_video_stub
  → MediaArtifactV1 + RenderReceiptV1 + DirectorPlanV1

PATH B — HyperFrames (full cinematic pipeline):
  ExecutionArtifactV1
  → DirectorPlanV1
  → director_to_html → HTMLCompositionV1
  → render_composition → result dict
  → MediaArtifactV1 + RenderReceiptV1 + DirectorPlanV1 + HTMLCompositionV1

No reasoning. No state mutation. Pure forward flow.
"""
from __future__ import annotations

from pathlib import Path
from typing import Literal, Optional, Tuple

from .contracts import canonical_json, sha256_hex
from .composition import HTMLCompositionV1, director_to_html
from .director import DirectorPlanV1, direct
from .models import ExecutionArtifactV1, MediaArtifactV1, RenderReceiptV1
from .receipts import make_render_receipt
from .renderer import RenderMode, render_composition
from .video import VideoRenderProfileV1, compile_video_spec, render_video_stub
from .audio import AudioRenderProfileV1, compile_audio_spec, render_audio_stub


def run_video_render(
    artifact:       ExecutionArtifactV1,
    profile:        VideoRenderProfileV1,
    previous_hash:  str,
    renderer_name:  str,
    director_style: str = "meditation",
    plan:           Optional[DirectorPlanV1] = None,
) -> Tuple[MediaArtifactV1, RenderReceiptV1, DirectorPlanV1]:
    """
    ExecutionArtifactV1 → (MediaArtifactV1, RenderReceiptV1, DirectorPlanV1).
    Returns the plan so callers can inspect creative decisions.
    Pure forward flow. No back-edge into kernel.
    """
    if plan is None:
        plan = direct(artifact, director_style)

    spec       = compile_video_spec(artifact, profile, plan=plan)
    input_hash = sha256_hex(canonical_json(spec))
    result     = render_video_stub(spec)

    media = MediaArtifactV1(
        media_id=            result["content_hash"],
        source_artifact_id=  artifact.artifact_id,
        source_receipt_hash= artifact.receipt_hash,
        kind=                "video",
        mime_type=           result["mime_type"],
        content_hash=        result["content_hash"],
        path=                result["path"],
        metadata=            result["metadata"],
    )

    receipt = make_render_receipt(
        run_id=              artifact.run_id,
        source_artifact_id=  artifact.artifact_id,
        source_receipt_hash= artifact.receipt_hash,
        render_kind=         "video",
        renderer=            renderer_name,
        input_hash=          input_hash,
        output_hash=         media.content_hash,
        previous_hash=       previous_hash,
    )

    return media, receipt, plan


def run_hyperframes_render(
    artifact:       ExecutionArtifactV1,
    previous_hash:  str,
    renderer_name:  str = "hyperframes",
    director_style: str = "meditation",
    plan:           Optional[DirectorPlanV1] = None,
    width:          int = 1920,
    height:         int = 1080,
    fps:            int = 30,
    mode:           RenderMode = "stub",
    output_dir:     Path = Path("artifacts/render"),
) -> Tuple[MediaArtifactV1, RenderReceiptV1, DirectorPlanV1, HTMLCompositionV1]:
    """
    Full cinematic pipeline (PATH B):
    ExecutionArtifactV1
    → DirectorPlanV1
    → HTMLCompositionV1
    → MediaArtifactV1 + RenderReceiptV1
    """
    if plan is None:
        plan = direct(artifact, director_style)

    comp   = director_to_html(plan, artifact, width=width, height=height, fps=fps)
    result = render_composition(comp, mode=mode, output_dir=output_dir)

    media = MediaArtifactV1(
        media_id=            result["content_hash"],
        source_artifact_id=  artifact.artifact_id,
        source_receipt_hash= artifact.receipt_hash,
        kind=                "video",
        mime_type=           result["mime_type"],
        content_hash=        result["content_hash"],
        path=                result["path"],
        metadata=            result["metadata"],
    )

    receipt = make_render_receipt(
        run_id=              artifact.run_id,
        source_artifact_id=  artifact.artifact_id,
        source_receipt_hash= artifact.receipt_hash,
        render_kind=         "video",
        renderer=            renderer_name,
        input_hash=          comp.composition_hash,
        output_hash=         media.content_hash,
        previous_hash=       previous_hash,
    )

    return media, receipt, plan, comp


def run_audio_render(
    artifact:      ExecutionArtifactV1,
    profile:       AudioRenderProfileV1,
    previous_hash: str,
    renderer_name: str,
) -> Tuple[MediaArtifactV1, RenderReceiptV1]:
    """ExecutionArtifactV1 → (MediaArtifactV1, RenderReceiptV1) for audio."""
    spec       = compile_audio_spec(artifact, profile)
    input_hash = sha256_hex(canonical_json(spec))
    result     = render_audio_stub(spec)

    media = MediaArtifactV1(
        media_id=            result["content_hash"],
        source_artifact_id=  artifact.artifact_id,
        source_receipt_hash= artifact.receipt_hash,
        kind=                "audio",
        mime_type=           result["mime_type"],
        content_hash=        result["content_hash"],
        path=                result["path"],
        metadata=            result["metadata"],
    )

    receipt = make_render_receipt(
        run_id=              artifact.run_id,
        source_artifact_id=  artifact.artifact_id,
        source_receipt_hash= artifact.receipt_hash,
        render_kind=         "audio",
        renderer=            renderer_name,
        input_hash=          input_hash,
        output_hash=         media.content_hash,
        previous_hash=       previous_hash,
    )

    return media, receipt
