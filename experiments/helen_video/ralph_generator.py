"""Ralph Generator — STUB. Candidate producer only. Cannot deliver.

Ralph imagines videos. HELEN admits them. This file generates candidates.
It has no delivery path. It cannot write to the video ledger directly.
It cannot call the delivery engine.

A real implementation would call Kling / Higgsfield / ffmpeg and return
a candidate dict. This stub returns metadata only — no actual rendering.

STUB STATUS: not implemented. Replace the body of generate_candidate()
when the render engine is wired.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone


def _sha256(data: str) -> str:
    return hashlib.sha256(data.encode()).hexdigest()


def generate_candidate(
    prompt: str,
    model: str = "helen-core",
    state_hash: str | None = None,
    ralph_iteration_id: str | None = None,
) -> dict:
    """Produce a video candidate descriptor. Does NOT render. Does NOT deliver.

    Returns a candidate dict for evaluation by admissibility_gate.
    The caller (not Ralph) decides whether to admit or reject.

    Receipt fields are NOT populated here — receipt extraction is a separate
    step performed after actual rendering.
    """
    candidate_id = _sha256(f"{prompt}:{model}:{datetime.now(timezone.utc).isoformat()}")
    return {
        "candidate_id": candidate_id,
        "ralph_iteration_id": ralph_iteration_id,
        "prompt": prompt,
        "model": model,
        "state_hash": state_hash,
        "ts": datetime.now(timezone.utc).isoformat(),
        "status": "CANDIDATE",
        "receipt": None,
        "_stub": True,
    }


def extract_receipt(candidate: dict, render_output: dict) -> dict:
    """Extract a receipt from actual render output.

    STUB: real implementation reads content_hash from rendered file,
    pipeline_hash from transform chain, visual_coherence and
    temporal_alignment from scoring model output.

    Args:
        candidate:     the candidate dict from generate_candidate()
        render_output: dict from the render engine (Kling/Higgsfield/ffmpeg)

    Returns:
        receipt dict suitable for admissibility_gate.evaluate()
    """
    raise NotImplementedError(
        "extract_receipt is not implemented. "
        "Wire a real render engine before calling this."
    )
