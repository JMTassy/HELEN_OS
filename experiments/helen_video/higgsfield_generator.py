"""Higgsfield Generator — MCP-backed video candidate producer.

Slots into the same interface as ralph_generator and remotion_wrapper.
Backend = Higgsfield AI via MCP at https://mcp.higgsfield.ai/mcp

Hard invariants (identical to all other generators):
  - Status is always CANDIDATE. Never ACCEPT, DELIVER, or ACTIVE.
  - Never writes to the ledger.
  - Never calls admissibility_gate.evaluate().
  - Never calls deliver() or any delivery function.
  - Receipt is produced after the job completes, bound to content_hash.

MCP transport:
  Real calls are deferred until you configure the Higgsfield connector
  in Claude settings (Settings → Connectors → Higgsfield, URL:
  https://mcp.higgsfield.ai/mcp). Until then, _invoke_higgsfield()
  raises NotImplementedError so the skeleton is safe to import and test.

Pipeline:
  prompt + model + params
    → _invoke_higgsfield()    (MCP call — async, polls until complete)
    → output URL / local path
    → sha256(content)         → content_hash
    → sha256(prompt)          → prompt_hash
    → sha256(content_hash + PIPELINE_SALT) → pipeline_hash
    → CANDIDATE + receipt
"""
from __future__ import annotations

import hashlib
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

from helen_video.admissibility_gate import PIPELINE_SALT

RENDERER = "higgsfield"

# Supported Higgsfield models (informational — passed through to MCP)
SUPPORTED_MODELS = frozenset({
    "kling-2.5",
    "veo-3",
    "sora-2",
    "seedance-2.0",
    "soul-cinema",
    "minimax-hailuo",
    "wan-2.6",
})


# ── hash helpers ──────────────────────────────────────────────────────────────

def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256_str(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()


def _canonical(obj: dict) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


def _prompt_hash(prompt: str) -> str:
    return _sha256_str(prompt)


def _pipeline_hash(content_hash: str) -> str:
    return _sha256_str(content_hash + PIPELINE_SALT)


def _content_hash_from_url(url: str) -> str:
    """Proxy hash when content is a remote URL (pre-download).

    Uses the URL string as content key until the file is fetched.
    Caller should recompute from actual bytes after download.
    """
    return _sha256_str(f"url:{url}")


def _content_hash_from_file(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


# ── MCP transport (deferred) ──────────────────────────────────────────────────

def _invoke_higgsfield(
    prompt: str,
    model: str,
    params: dict | None,
    output_path: Path | None,
) -> dict:
    """Submit a generation job to Higgsfield via MCP and wait for result.

    SKELETON: raises NotImplementedError until the MCP connector is wired.

    When implemented, this should:
      1. Call generate_video(prompt=..., model=..., **params)
      2. Poll until job status = complete (async MCP pattern)
      3. Return {"url": str, "job_id": str, "model": str, "duration": float}

    Args:
        prompt:      Text prompt for video generation.
        model:       Higgsfield model ID (e.g. "kling-2.5", "soul-cinema").
        params:      Optional generation params (aspect_ratio, duration, seed…).
        output_path: If provided, caller will download URL here after return.

    Returns:
        dict with at least {"url": str, "job_id": str}

    Raises:
        NotImplementedError: until MCP connector is configured.
        RuntimeError: if the MCP call fails or job is rejected.
    """
    raise NotImplementedError(
        "Higgsfield MCP connector not yet configured. "
        "Add the connector in Claude Settings → Connectors → Higgsfield "
        "(URL: https://mcp.higgsfield.ai/mcp), then implement this function "
        "to call generate_video() and poll for completion."
    )


# ── public API ────────────────────────────────────────────────────────────────

def generate_candidate(
    prompt: str,
    model: str = "kling-2.5",
    params: dict | None = None,
    output_path: str | Path | None = None,
    video_id: str | None = None,
) -> dict:
    """Submit a Higgsfield generation job and return a gate-ready CANDIDATE.

    Args:
        prompt:      Text prompt for the video.
        model:       Higgsfield model ID. Default: "kling-2.5".
        params:      Optional generation params dict (aspect_ratio, seed, etc.)
        output_path: Optional local path to download the result.
        video_id:    Optional stable ID; generated if not provided.

    Returns:
        CANDIDATE dict with receipt. Status is always "CANDIDATE".
        Pass receipt to admissibility_gate.evaluate() when ready.

    Raises:
        NotImplementedError: if Higgsfield MCP connector is not wired.
        RuntimeError: if the generation job fails.
    """
    out = Path(output_path) if output_path else None

    job_result = _invoke_higgsfield(prompt, model, params, out)

    url = job_result.get("url", "")
    job_id = job_result.get("job_id", str(uuid.uuid4()))

    # Content hash: from local file if downloaded, else from URL proxy
    if out and out.exists():
        content_hash = _content_hash_from_file(out)
    else:
        content_hash = _content_hash_from_url(url)

    ph = _pipeline_hash(content_hash)
    pph = _prompt_hash(prompt)
    ts = datetime.now(timezone.utc).isoformat()
    vid = video_id or str(uuid.uuid4())

    receipt = {
        "content_hash": content_hash,
        "pipeline_hash": ph,
        "renderer": RENDERER,
        "model": model,
        "prompt_hash": pph,
        "job_id": job_id,
        "source_url": url,
        "timestamp": ts,
    }

    return {
        "video_id": vid,
        "status": "CANDIDATE",
        "source": RENDERER,
        "model": model,
        "prompt": prompt,
        "job_id": job_id,
        "output_path": str(out) if out else None,
        "source_url": url,
        "content_hash": content_hash,
        "receipt": receipt,
    }


def build_receipt_from_result(
    job_result: dict,
    prompt: str,
    model: str,
    local_file: str | Path | None = None,
) -> dict:
    """Build a receipt from a completed Higgsfield job result.

    Use when the job ran externally and you only need the receipt.
    Mirrors remotion_wrapper.build_receipt_from_file().

    Args:
        job_result:  Dict with at least {"url": str, "job_id": str}.
        prompt:      The prompt that produced this result.
        model:       The model used.
        local_file:  If the file was downloaded, pass the path for exact hashing.
    """
    url = job_result.get("url", "")
    job_id = job_result.get("job_id", "")

    if local_file:
        content_hash = _content_hash_from_file(Path(local_file))
    else:
        content_hash = _content_hash_from_url(url)

    return {
        "content_hash": content_hash,
        "pipeline_hash": _pipeline_hash(content_hash),
        "renderer": RENDERER,
        "model": model,
        "prompt_hash": _prompt_hash(prompt),
        "job_id": job_id,
        "source_url": url,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
