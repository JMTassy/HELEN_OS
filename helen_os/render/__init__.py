"""
helen_os.render — Embodiment layer.

Pure function of execution output. No reasoning. No state mutation.
Position in pipeline: after E (execution), never before.

  C (cognition) → G (governor) → E (execution) → receipt → render

render.video   — MP4 via HyperFrames
render.voice   — WAV via Gemini TTS (thin wrapper, re-exported)

Law:
  - RenderRequest must carry a receipt_hash binding it to the ledger
  - Render functions are deterministic: same input → same output bytes
  - No hidden prompts, no independent reasoning, no tool calls
  - authority: False always — rendering ≠ truth
"""
from helen_os.render.video import (
    RenderRequest, RenderScript, ScriptSegment,
    RenderReceipt, render_video, assemble_from_ledger, new_render_id,
)

__all__ = [
    "RenderRequest", "RenderScript", "ScriptSegment",
    "RenderReceipt", "render_video", "assemble_from_ledger", "new_render_id",
]
