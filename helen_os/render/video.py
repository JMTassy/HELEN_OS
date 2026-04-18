"""
helen_os.render.video — Video embodiment layer.

Canonical position: after E (execution), never before.

  C → G → E → Execution Artifact → Render Contract → Video → Render Receipt

Renderer may:  transform, stylize, materialize media
Renderer may NOT: reason, decide, mutate governed state, call tools, read memory

Canonical objects:
  RenderScript        — structured script with typed segments
  RenderRequest       — RENDER_REQUEST_V1, bound to source artifact hash
  RenderReceipt       — post-render provenance, bound to render_request_hash
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal, Optional

REPO_ROOT       = Path(__file__).resolve().parents[2]
TEMPLATE_DIR    = REPO_ROOT / "oracle_town/skills/video/hyperframes/templates/meditation"
ARTIFACTS_MEDIA = REPO_ROOT / "artifacts/media"
GENERATOR       = TEMPLATE_DIR / "generate_meditation.py"

VALID_MODES    = frozenset({"video", "audio", "preview"})
VALID_PROFILES = frozenset({
    "helen_meditation_soft",
    "helen_oracle_precise",
    "helen_temple_symbolic",
    "helen_mayor_formal",
    "helen_narrator_warm",
})
VALID_SEGMENT_KINDS = frozenset({"paragraph", "heading", "pause", "receipt_line"})


# ── Script objects ────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class ScriptSegment:
    """One typed unit of content in a render script."""
    kind: Literal["paragraph", "heading", "pause", "receipt_line"]
    text: str = ""
    duration_hint: float = 0.0  # seconds, 0 = auto from text length

    def __post_init__(self) -> None:
        if self.kind not in VALID_SEGMENT_KINDS:
            raise ValueError(f"segment kind must be one of {VALID_SEGMENT_KINDS}")


@dataclass(frozen=True)
class RenderScript:
    """
    Structured script consumed by the renderer.
    Segments are typed so the renderer can apply per-kind styling.
    """
    title:    str
    body:     str                          # full plain text (for TTS)
    segments: tuple[ScriptSegment, ...]   # structured for visual layout


# ── Canonical contract: RENDER_REQUEST_V1 ─────────────────────────────────────

@dataclass(frozen=True)
class RenderRequest:
    """
    RENDER_REQUEST_V1 — typed contract between execution output and renderer.

    Produced by: E layer (execution), or an assembler that reads from the ledger.
    Consumed by: render_video() — pure function, no side effects.

    source_artifact_hash binds this request to a specific execution artifact.
    Without it, the render has no ledger provenance — rejected at construction.
    authority is structurally False: rendering ≠ truth.
    """
    render_id:            str           # "rr_<uuid4_hex[:12]>"
    source_artifact_type: str           # e.g. "EXECUTION_RESULT_V1", "RUN_SUMMARY_V1"
    source_artifact_hash: str           # sha256: of the source — mandatory ledger binding
    mode:                 str           # video | audio | preview
    profile:              str           # helen_meditation_soft | helen_oracle_precise | …
    script:               RenderScript
    date:                 str           # ISO YYYY-MM-DD
    commit_sha:           str = ""
    commit_repo:          str = ""
    schema_name:          str = "RENDER_REQUEST_V1"
    authority:            bool = False  # always False — enforce at construction

    def __post_init__(self) -> None:
        if self.authority:
            raise ValueError("RENDER_REQUEST_V1.authority must be False — render ≠ truth")
        if not self.source_artifact_hash.startswith("sha256:"):
            raise ValueError("source_artifact_hash must be sha256: prefixed")
        if self.mode not in VALID_MODES:
            raise ValueError(f"mode must be one of {VALID_MODES}")
        if self.profile not in VALID_PROFILES:
            raise ValueError(f"profile must be one of {VALID_PROFILES}")
        if not self.render_id.startswith("rr_"):
            raise ValueError("render_id must start with 'rr_'")

    def to_dict(self) -> dict:
        return {
            "schema_name":          self.schema_name,
            "render_id":            self.render_id,
            "source_artifact_type": self.source_artifact_type,
            "source_artifact_hash": self.source_artifact_hash,
            "mode":                 self.mode,
            "profile":              self.profile,
            "script": {
                "title":    self.script.title,
                "body":     self.script.body,
                "segments": [
                    {"kind": s.kind, "text": s.text, "duration_hint": s.duration_hint}
                    for s in self.script.segments
                ],
            },
            "date":        self.date,
            "commit_sha":  self.commit_sha,
            "commit_repo": self.commit_repo,
            "authority":   "NONE",
        }

    def request_hash(self) -> str:
        """sha256: of the canonical request dict — used in RenderReceipt."""
        return "sha256:" + hashlib.sha256(
            json.dumps(self.to_dict(), sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()


# ── Render receipt ─────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class RenderReceipt:
    """
    Post-render provenance. Closes the chain:
      source_artifact_hash → render_request_hash → render_receipt.

    Immutable. authority=False always.
    """
    schema_name:          str  = "RENDER_RECEIPT_V1"
    render_id:            str  = ""
    render_request_hash:  str  = ""   # sha256: of RenderRequest.to_dict()
    source_artifact_hash: str  = ""   # echoed — chain is explicit
    ok:                   bool = False
    video_path:           Optional[Path] = None
    render_sha:           Optional[str]  = None   # sha256: of MP4 bytes
    provenance_hash:      Optional[str]  = None   # sha256: of provenance.json
    rendered_at:          str  = ""
    error:                Optional[str]  = None
    authority:            bool = False

    def __post_init__(self) -> None:
        if self.authority:
            raise ValueError("RENDER_RECEIPT_V1.authority must be False")

    def to_dict(self) -> dict:
        return {
            "schema_name":          self.schema_name,
            "render_id":            self.render_id,
            "render_request_hash":  self.render_request_hash,
            "source_artifact_hash": self.source_artifact_hash,
            "ok":                   self.ok,
            "video_path":           str(self.video_path) if self.video_path else None,
            "render_sha":           self.render_sha,
            "provenance_hash":      self.provenance_hash,
            "rendered_at":          self.rendered_at,
            "error":                self.error,
            "authority":            "NONE",
        }


# ── Helpers ───────────────────────────────────────────────────────────────────

def _sha256(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def new_render_id() -> str:
    return "rr_" + uuid.uuid4().hex[:12]


def _profile_to_tone(profile: str) -> str:
    return {
        "helen_meditation_soft":  "reflective",
        "helen_oracle_precise":   "serious",
        "helen_temple_symbolic":  "symbolic",
        "helen_mayor_formal":     "calm",
        "helen_narrator_warm":    "calm",
    }.get(profile, "calm")


# ── Main render function ──────────────────────────────────────────────────────

def render_video(
    req: RenderRequest,
    *,
    output_path: Optional[Path] = None,
    dry_run: bool = False,
    timeout: int = 600,
) -> RenderReceipt:
    """
    Pure function: RenderRequest → RenderReceipt.

    Deterministic: same request → same output bytes.
    Subprocess only — no LLM, no state mutation, no tool calls.
    """
    if not GENERATOR.exists():
        return RenderReceipt(
            render_id=req.render_id,
            render_request_hash=req.request_hash(),
            source_artifact_hash=req.source_artifact_hash,
            ok=False,
            rendered_at=_now(),
            error=f"Generator not found: {GENERATOR}",
        )

    ARTIFACTS_MEDIA.mkdir(parents=True, exist_ok=True)

    date_slug  = req.date.replace("-", "")
    topic_slug = "".join(c if c.isalnum() else "_"
                         for c in req.script.title.lower())[:30]

    if output_path is None:
        output_path = ARTIFACTS_MEDIA / f"{date_slug}__{topic_slug}.mp4"

    # Build meditation.config.json from request
    cfg = {
        "date":            req.date,
        "topic":           req.script.title,
        "meditation_text": req.script.body,
        "run_hash":        req.source_artifact_hash,
        "commit_sha":      req.commit_sha,
        "commit_repo":     req.commit_repo,
        "authority":       "NONE",
        "tone":            _profile_to_tone(req.profile),
    }

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".json", delete=False, prefix="helen_render_"
    ) as f:
        json.dump(cfg, f, indent=2)
        config_path = Path(f.name)

    try:
        cmd = [sys.executable, str(GENERATOR),
               "--config", str(config_path),
               "--output", str(output_path)]
        if dry_run:
            cmd.append("--dry-run")

        result = subprocess.run(
            cmd, cwd=str(TEMPLATE_DIR),
            env={**os.environ},
            capture_output=True, text=True, timeout=timeout,
        )

        rendered_at = _now()

        if result.returncode != 0:
            return RenderReceipt(
                render_id=req.render_id,
                render_request_hash=req.request_hash(),
                source_artifact_hash=req.source_artifact_hash,
                ok=False, rendered_at=rendered_at,
                error=f"exit {result.returncode}:\n{result.stderr[-600:]}",
            )

        if dry_run or not output_path.exists():
            return RenderReceipt(
                render_id=req.render_id,
                render_request_hash=req.request_hash(),
                source_artifact_hash=req.source_artifact_hash,
                ok=True, rendered_at=rendered_at,
            )

        render_sha = _sha256(output_path)
        prov_path  = output_path.with_suffix(".provenance.json")
        prov_hash  = _sha256(prov_path) if prov_path.exists() else None

        return RenderReceipt(
            render_id=req.render_id,
            render_request_hash=req.request_hash(),
            source_artifact_hash=req.source_artifact_hash,
            ok=True,
            video_path=output_path,
            render_sha=render_sha,
            provenance_hash=prov_hash,
            rendered_at=rendered_at,
        )

    except subprocess.TimeoutExpired:
        return RenderReceipt(
            render_id=req.render_id,
            render_request_hash=req.request_hash(),
            source_artifact_hash=req.source_artifact_hash,
            ok=False, rendered_at=_now(),
            error=f"timeout after {timeout}s",
        )
    except Exception as exc:
        return RenderReceipt(
            render_id=req.render_id,
            render_request_hash=req.request_hash(),
            source_artifact_hash=req.source_artifact_hash,
            ok=False, rendered_at=_now(),
            error=str(exc),
        )
    finally:
        config_path.unlink(missing_ok=True)


# ── Assembler: ledger → RenderRequest ─────────────────────────────────────────

def assemble_from_ledger(
    run_id: str,
    ledger_entries: list[dict],
    *,
    date: Optional[str] = None,
    profile: str = "helen_narrator_warm",
) -> RenderRequest:
    """
    Build a RENDER_REQUEST_V1 from receipted ledger entries.
    No LLM — script assembled deterministically from ledger facts only.
    """
    admitted = [e for e in ledger_entries if e.get("decision") == "ADMITTED"]
    rejected = [e for e in ledger_entries if e.get("decision") == "REJECTED"]

    segments: list[ScriptSegment] = []
    lines:    list[str]           = []

    heading = f"Run {run_id[:12]}"
    segments.append(ScriptSegment(kind="heading", text=heading))

    if admitted:
        text = (
            f"{len(admitted)} skill{'s' if len(admitted) != 1 else ''} admitted: "
            + ", ".join(e.get("skill_id", "unknown") for e in admitted) + "."
        )
        segments.append(ScriptSegment(kind="paragraph", text=text))
        lines.append(text)

    if rejected:
        text = f"{len(rejected)} proposal{'s' if len(rejected) != 1 else ''} rejected by constitutional gates."
        segments.append(ScriptSegment(kind="paragraph", text=text))
        lines.append(text)

    seal = "No receipt — no claim. All of it is in the ledger."
    segments.append(ScriptSegment(kind="paragraph", text=seal))
    lines.append(seal)

    # receipt_line shows the run hash
    source_hash = "sha256:" + hashlib.sha256(
        json.dumps(ledger_entries, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    segments.append(ScriptSegment(kind="receipt_line", text=source_hash))

    body = " ".join(lines)

    return RenderRequest(
        render_id=new_render_id(),
        source_artifact_type="RUN_LEDGER_V1",
        source_artifact_hash=source_hash,
        mode="video",
        profile=profile,
        script=RenderScript(
            title=f"Run {run_id[:12]}",
            body=body,
            segments=tuple(segments),
        ),
        date=date or _now()[:10],
    )
