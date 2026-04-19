"""
HELEN STORYBOARD_V1 — deterministic decomposition of narrative into timed scenes.

Pipeline position:
  SCRIPT → STORYBOARD_V1 → RENDER_REQUEST_V1 → HTML+GSAP → VIDEO

Core principle: Storyboard = deterministic decomposition of narrative into timed scenes.
No AI. No interpretation. No freedom.

Rules:
  1. FULL COVERAGE: sum(duration_i) == duration_total
  2. NO OVERLAP: scenes are sequential, no time overlap
  3. AUDIO FIRST: visual follows narration timing
  4. NO INTERPRETATION: storyboard cannot invent meaning
"""
from __future__ import annotations

import hashlib
import json
import datetime
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from helen_os.render.contract import (
    RenderRequest, Segment, _canon, _sha256, _now_utc,
)
from helen_os.render.director import (
    CAMERAS, TRANSITIONS, TEXT_MOTIONS, VISUAL_DNA, EMOTIONS,
)


# ── Constants ─────────────────────────────────────────────────────────────────

VISUAL_TYPES = frozenset({"abstract", "human", "energy", "nature"})
CAMERA_MOTIONS = frozenset({"none", "slow_push", "drift", "zoom_out", "pull_back", "orbit"})
TEXT_OVERLAY_STYLES = frozenset({"soft_center", "subtitle", "minimal"})
TRANSITION_TYPES = frozenset({"fade", "crossfade", "none", "dissolve"})

# Map storyboard camera motions → director camera keys for HTML composition
_CAMERA_MAP = {
    "none":      "static_breathe",
    "slow_push": "slow_push_in",
    "drift":     "drift_right",
    "zoom_out":  "slow_pull_out",
    "pull_back": "slow_pull_out",
    "orbit":     "drift_left",
}

# Map storyboard transitions → director transition keys
_TRANSITION_MAP = {
    "fade":      "fade_black",
    "crossfade": "crossfade",
    "none":      "hard_cut",
    "dissolve":  "blur_cross",
}

# Map text overlay styles → director text motion + position
_TEXT_STYLE_MAP = {
    "soft_center": {"motion": "blur_reveal", "position": "center"},
    "subtitle":    {"motion": "fade",        "position": "bottom"},
    "minimal":     {"motion": "fade",        "position": "bottom"},
}


# ── Tolerance ─────────────────────────────────────────────────────────────────

_EPSILON = 1e-6  # float comparison tolerance for coverage check


# ── StoryboardScene ───────────────────────────────────────────────────────────

@dataclass
class StoryboardScene:
    """
    A single timed scene in the storyboard.

    Every field is STRICT — no optional semantics, no inference.
    The scene owns a contiguous, non-overlapping time slot.
    """
    scene_id:       str
    start:          float                   # seconds from video start
    duration:       float                   # seconds
    narration:      Dict[str, Any]          # {"text": str, "audio_ref": str}
    visual:         Dict[str, Any]          # {"type": str, "description": str, "assets": list}
    camera:         Dict[str, Any]          # {"motion": str, "zoom": float}
    text_overlay:   Dict[str, Any]          # {"enabled": bool, "content": str, "style": str}
    emotion:        str
    transition_out: str                     # fade|crossfade|none|dissolve

    def __post_init__(self) -> None:
        if self.duration <= 0:
            raise ValueError(f"Scene {self.scene_id}: duration must be > 0, got {self.duration}")
        if self.start < 0:
            raise ValueError(f"Scene {self.scene_id}: start must be >= 0, got {self.start}")

    @property
    def end(self) -> float:
        return self.start + self.duration

    def to_dict(self) -> Dict[str, Any]:
        return {
            "scene_id":       self.scene_id,
            "start":          self.start,
            "duration":       self.duration,
            "narration":      self.narration,
            "visual":         self.visual,
            "camera":         self.camera,
            "text_overlay":   self.text_overlay,
            "emotion":        self.emotion,
            "transition_out": self.transition_out,
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> StoryboardScene:
        return cls(
            scene_id=d["scene_id"],
            start=float(d["start"]),
            duration=float(d["duration"]),
            narration=d["narration"],
            visual=d["visual"],
            camera=d["camera"],
            text_overlay=d["text_overlay"],
            emotion=d["emotion"],
            transition_out=d["transition_out"],
        )


# ── Storyboard ────────────────────────────────────────────────────────────────

@dataclass
class Storyboard:
    """
    STORYBOARD_V1 — deterministic scene plan between Script and Renderer.

    Invariants:
      - type is always "STORYBOARD_V1"
      - source_script_hash is sha256 of the original script text
      - sum(scene.duration) == duration_total
      - scenes are sequential with no overlap
      - every scene has narration text (no interpretation rule)
    """
    type:               str = "STORYBOARD_V1"
    storyboard_id:      str = ""
    source_script_hash: str = ""
    duration_total:     float = 0.0
    aspect_ratio:       str = "16:9"
    scenes:             List[StoryboardScene] = field(default_factory=list)

    # ── Validation ────────────────────────────────────────────────────────────

    def validate(self) -> List[str]:
        """
        Check all four storyboard rules.

        Returns a list of violation strings. Empty list = valid storyboard.

        Rules checked:
          1. FULL COVERAGE  — sum(duration_i) == duration_total
          2. NO OVERLAP     — scenes are sequential, each starts where the previous ends
          3. AUDIO FIRST    — every scene has narration text (visual follows narration)
          4. NO INTERPRETATION — proxy: every scene has non-empty narration text
        """
        violations: List[str] = []

        if not self.scenes:
            violations.append("EMPTY: storyboard has no scenes")
            return violations

        # Rule 1: FULL COVERAGE
        scene_sum = sum(s.duration for s in self.scenes)
        if abs(scene_sum - self.duration_total) > _EPSILON:
            violations.append(
                f"FULL_COVERAGE: sum(duration)={scene_sum:.6f} != "
                f"duration_total={self.duration_total:.6f}"
            )

        # Rule 2: NO OVERLAP — scenes must tile sequentially
        for i, scene in enumerate(self.scenes):
            if i == 0:
                if abs(scene.start) > _EPSILON:
                    violations.append(
                        f"NO_OVERLAP: scene[0] starts at {scene.start}, expected 0.0"
                    )
            else:
                expected_start = self.scenes[i - 1].start + self.scenes[i - 1].duration
                if abs(scene.start - expected_start) > _EPSILON:
                    violations.append(
                        f"NO_OVERLAP: scene[{i}] starts at {scene.start:.6f}, "
                        f"expected {expected_start:.6f} (gap or overlap)"
                    )

        # Rule 3 + 4: AUDIO FIRST / NO INTERPRETATION
        # Proxy: every scene must have non-empty narration text
        for i, scene in enumerate(self.scenes):
            narration_text = scene.narration.get("text", "").strip()
            if not narration_text:
                violations.append(
                    f"AUDIO_FIRST: scene[{i}] ({scene.scene_id}) has empty narration text"
                )

        # Field validation: visual type
        for i, scene in enumerate(self.scenes):
            vtype = scene.visual.get("type", "")
            if vtype and vtype not in VISUAL_TYPES:
                violations.append(
                    f"SCHEMA: scene[{i}] visual.type '{vtype}' not in {sorted(VISUAL_TYPES)}"
                )

        # Field validation: camera motion
        for i, scene in enumerate(self.scenes):
            motion = scene.camera.get("motion", "")
            if motion and motion not in CAMERA_MOTIONS:
                violations.append(
                    f"SCHEMA: scene[{i}] camera.motion '{motion}' not in {sorted(CAMERA_MOTIONS)}"
                )

        # Field validation: transition_out
        for i, scene in enumerate(self.scenes):
            if scene.transition_out not in TRANSITION_TYPES:
                violations.append(
                    f"SCHEMA: scene[{i}] transition_out '{scene.transition_out}' "
                    f"not in {sorted(TRANSITION_TYPES)}"
                )

        # Field validation: text_overlay style
        for i, scene in enumerate(self.scenes):
            if scene.text_overlay.get("enabled"):
                style = scene.text_overlay.get("style", "")
                if style and style not in TEXT_OVERLAY_STYLES:
                    violations.append(
                        f"SCHEMA: scene[{i}] text_overlay.style '{style}' "
                        f"not in {sorted(TEXT_OVERLAY_STYLES)}"
                    )

        return violations

    # ── Serialization ─────────────────────────────────────────────────────────

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type":               self.type,
            "storyboard_id":      self.storyboard_id,
            "source_script_hash": self.source_script_hash,
            "duration_total":     self.duration_total,
            "aspect_ratio":       self.aspect_ratio,
            "scenes":             [s.to_dict() for s in self.scenes],
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> Storyboard:
        return cls(
            type=d.get("type", "STORYBOARD_V1"),
            storyboard_id=d["storyboard_id"],
            source_script_hash=d["source_script_hash"],
            duration_total=float(d["duration_total"]),
            aspect_ratio=d.get("aspect_ratio", "16:9"),
            scenes=[StoryboardScene.from_dict(s) for s in d["scenes"]],
        )

    def storyboard_hash(self) -> str:
        """Deterministic hash of the full storyboard content."""
        return _sha256(_canon(self.to_dict()))

    # ── Conversion: → RENDER_REQUEST_V1 ──────────────────────────────────────

    def to_render_request(self, render_id: str = "", mode: str = "video",
                          profile: str = "helen_default",
                          voice: str = "Zephyr") -> RenderRequest:
        """
        Convert storyboard to RENDER_REQUEST_V1 for the renderer.

        Each scene becomes a Segment. The full narration text becomes body.
        """
        if not render_id:
            render_id = f"rr_{self.storyboard_hash()[:12]}"

        segments: List[Segment] = []
        for scene in self.scenes:
            segments.append(Segment(
                kind="paragraph",
                text=scene.narration.get("text", ""),
                duration_hint=scene.duration,
            ))

        body = "\n\n".join(
            scene.narration.get("text", "") for scene in self.scenes
        )

        return RenderRequest(
            render_id=render_id,
            source_artifact_type="STORYBOARD_V1",
            source_artifact_hash=self.storyboard_hash(),
            mode=mode,
            profile=profile,
            title=self.storyboard_id,
            body=body,
            segments=segments,
            voice=voice,
            resolution=(1080, 1920),
            fps=30,
            authority="NONE",
        )

    # ── Conversion: → HTML+GSAP Composition ──────────────────────────────────

    def to_html_composition(self) -> str:
        """
        Generate an HTML+GSAP composition from the storyboard.

        Builds on director.py patterns: each scene becomes a positioned div
        with camera, text overlay, and transition data attributes.
        The output is a self-contained HTML document ready for frame capture.
        """
        palette = VISUAL_DNA["palette"]
        scenes_html: List[str] = []

        for i, scene in enumerate(self.scenes):
            # Resolve camera
            camera_key = _CAMERA_MAP.get(
                scene.camera.get("motion", "none"), "static_breathe"
            )
            zoom = scene.camera.get("zoom", 1.0)

            # Resolve transition
            transition_key = _TRANSITION_MAP.get(
                scene.transition_out, "crossfade"
            )

            # Resolve text overlay
            overlay = scene.text_overlay
            text_style = _TEXT_STYLE_MAP.get(
                overlay.get("style", "soft_center"),
                _TEXT_STYLE_MAP["soft_center"],
            )

            # Emotion → color accent
            emotion_colors = {
                "calm": palette.get("gold", "#c9a961"),
                "vulnerable": palette.get("rose", "#c86482"),
                "powerful": palette.get("red", "#e84855"),
                "intimate": palette.get("violet", "#783cb4"),
                "ascending": palette.get("cyan", "#22d3ee"),
                "breaking": palette.get("dim", "#504666"),
                "warm": palette.get("gold", "#c9a961"),
            }
            color = emotion_colors.get(scene.emotion, palette.get("white", "#e6e6f0"))

            # Visual type → background hint
            visual_type = scene.visual.get("type", "abstract")
            assets = scene.visual.get("assets", [])
            bg_asset = assets[0] if assets else f"assets/scene_{i}.png"

            block = f'''
    <div class="scene" id="{scene.scene_id}"
         data-start="{scene.start:.1f}" data-duration="{scene.duration:.1f}"
         data-camera="{camera_key}" data-zoom="{zoom:.2f}"
         data-emotion="{scene.emotion}" data-visual-type="{visual_type}"
         data-transition="{transition_key}">
      <div class="scene-bg" style="background-image:url('{bg_asset}')"></div>
      <div class="scene-overlay"></div>'''

            if overlay.get("enabled", False):
                content = overlay.get("content", "") or scene.narration.get("text", "")
                position = text_style["position"]
                motion = text_style["motion"]
                block += f'''
      <div class="text-block {position}" data-motion="{motion}"
           data-delay="0.8" style="color:{color}">
        {content}
      </div>'''

            block += '''
    </div>'''
            scenes_html.append(block)

        # Aspect ratio → dimensions
        if self.aspect_ratio == "9:16":
            width, height = 1080, 1920
        elif self.aspect_ratio == "1:1":
            width, height = 1080, 1080
        else:  # 16:9
            width, height = 1920, 1080

        html = f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>{self.storyboard_id}</title>
  <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
  <style>
    html, body {{ margin:0; width:{width}px; height:{height}px; background:#06080e; overflow:hidden; }}
    .scene {{ position:absolute; inset:0; opacity:0; }}
    .scene-bg {{ position:absolute; inset:-60px; width:calc(100% + 120px); height:calc(100% + 120px);
                 background-size:cover; background-position:center; }}
    .scene-overlay {{ position:absolute; inset:0;
                      background:linear-gradient(to bottom, transparent 50%, rgba(6,8,14,0.8) 100%); }}
    .text-block {{ position:absolute; width:100%; text-align:center; padding:0 60px; box-sizing:border-box;
                   font-family:'Helvetica Neue',sans-serif; font-size:28px; line-height:1.6; opacity:0; }}
    .text-block.bottom {{ bottom:15%; }}
    .text-block.center {{ top:50%; transform:translateY(-50%); }}
    .text-block.top {{ top:15%; }}
  </style>
</head>
<body>
  <div id="root" data-composition-id="{self.storyboard_id}"
       data-width="{width}" data-height="{height}"
       data-start="0" data-duration="{self.duration_total:.1f}">
{"".join(scenes_html)}
    <audio data-start="0" data-duration="{self.duration_total:.1f}" data-volume="1">
      <source src="voiceover.wav" type="audio/wav" />
    </audio>
  </div>
</body>
</html>'''
        return html


# ── Builder: from_script ──────────────────────────────────────────────────────

def from_script(script_text: str, segments: List[Dict[str, Any]]) -> Storyboard:
    """
    Build a Storyboard from a script and segment timing info.

    This is the canonical entry point. Deterministic: same inputs → same output.

    Args:
        script_text: The full script text (hashed for provenance).
        segments: List of dicts, each with:
            - text (str): narration text for the scene
            - duration (float): scene duration in seconds
            - emotion (str): emotion label
            - visual_type (str): abstract|human|energy|nature
            - visual_description (str): what the visual should depict
            - camera_motion (str): none|slow_push|drift|zoom_out|pull_back|orbit
            - transition (str): fade|crossfade|none|dissolve

    Returns:
        A fully populated, validated Storyboard.
    """
    script_hash = hashlib.sha256(script_text.encode("utf-8")).hexdigest()
    storyboard_id = f"sb_{script_hash[:12]}"

    scenes: List[StoryboardScene] = []
    cursor = 0.0

    for i, seg in enumerate(segments):
        duration = float(seg["duration"])
        text = seg["text"]
        emotion = seg.get("emotion", "calm")
        visual_type = seg.get("visual_type", "abstract")
        visual_desc = seg.get("visual_description", "")
        camera_motion = seg.get("camera_motion", "none")
        transition = seg.get("transition", "fade")

        # Default zoom based on camera motion
        zoom_defaults = {
            "none": 1.0,
            "slow_push": 1.08,
            "drift": 1.05,
            "zoom_out": 0.92,
            "pull_back": 0.95,
            "orbit": 1.03,
        }
        zoom = zoom_defaults.get(camera_motion, 1.0)

        scene = StoryboardScene(
            scene_id=f"sc_{i:03d}",
            start=round(cursor, 6),
            duration=round(duration, 6),
            narration={
                "text": text,
                "audio_ref": f"audio/scene_{i:03d}.wav",
            },
            visual={
                "type": visual_type,
                "description": visual_desc,
                "assets": [],
            },
            camera={
                "motion": camera_motion,
                "zoom": zoom,
            },
            text_overlay={
                "enabled": True,
                "content": "",
                "style": "soft_center" if i == 0 else "subtitle",
            },
            emotion=emotion,
            transition_out=transition,
        )
        scenes.append(scene)
        cursor += duration

    duration_total = round(cursor, 6)

    return Storyboard(
        type="STORYBOARD_V1",
        storyboard_id=storyboard_id,
        source_script_hash=script_hash,
        duration_total=duration_total,
        aspect_ratio="16:9",
        scenes=scenes,
    )


# ── STORYBOARD_RECEIPT_V1 ────────────────────────────────────────────────────

@dataclass
class StoryboardReceipt:
    """
    Receipt for a materialized storyboard.

    Proves: this storyboard was built, validated, and its outputs hashed.
    Authority is always NONE — the storyboard layer has no sovereign power.
    """
    storyboard_id:      str
    source_script_hash: str
    scene_count:        int
    duration_total:     float
    output_hashes:      List[str]
    timestamp:          str = ""
    authority:          str = "NONE"

    def __post_init__(self) -> None:
        if self.authority != "NONE":
            raise ValueError(f"StoryboardReceipt.authority must be NONE, got {self.authority}")
        if not self.timestamp:
            self.timestamp = _now_utc()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type":               "STORYBOARD_RECEIPT_V1",
            "storyboard_id":      self.storyboard_id,
            "source_script_hash": self.source_script_hash,
            "scene_count":        self.scene_count,
            "duration_total":     self.duration_total,
            "output_hashes":      self.output_hashes,
            "timestamp":          self.timestamp,
            "authority":          self.authority,
        }

    def receipt_hash(self) -> str:
        return _sha256(_canon(self.to_dict()))

    @classmethod
    def from_storyboard(cls, sb: Storyboard,
                        output_hashes: Optional[List[str]] = None) -> StoryboardReceipt:
        """Build a receipt from a validated storyboard."""
        sb_hash = sb.storyboard_hash()
        return cls(
            storyboard_id=sb.storyboard_id,
            source_script_hash=sb.source_script_hash,
            scene_count=len(sb.scenes),
            duration_total=sb.duration_total,
            output_hashes=output_hashes or [sb_hash],
        )
