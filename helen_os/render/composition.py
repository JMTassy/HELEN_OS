"""
HELEN Render — HTML_COMPOSITION_V1.

The HyperFrames layer. Video = structured data + rendering.

Chain:
  DirectorPlanV1
  → director_to_html(plan, artifact)  → HTMLCompositionV1
  → render_composition(comp)          → MP4 path
  → MediaArtifactV1 + RenderReceiptV1

Invariants:
  C1: same plan + artifact → same HTML (deterministic)
  C2: authority=False always
  C3: composition_hash = sha256(html + canonical(assets))
  C4: composition carries plan_hash + source_receipt_hash (full provenance chain)

HELEN Visual DNA (constitutional — never deviate):
  background: #050a1a  (deep blue/black)
  accent:     #d4a843  (amber/gold)
  motion:     slow, intentional — camera always drifting
  light:      volumetric, dust particles
  text:       Cormorant Garamond — weight without aggression
  pacing:     breath-driven — silence is content
"""
from __future__ import annotations

import dataclasses
import textwrap
from dataclasses import dataclass, field
from typing import Any, Dict, List

from .contracts import canonical_json, sha256_hex
from .director import DirectorPlanV1, Shot, CameraMove
from .models import ExecutionArtifactV1


# ── Asset ──────────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class Asset:
    asset_id: str
    type:     str    # "audio" | "image" | "video" | "font"
    src:      str    # path or data-uri placeholder


# ── HTMLCompositionV1 ──────────────────────────────────────────────────────────

@dataclass(frozen=True)
class HTMLCompositionV1:
    """
    Typed HTML document + asset manifest.
    Same plan + artifact → same bytes (C1).
    authority=False always (C2).
    """
    type:                str   # always "HTML_COMPOSITION_V1"
    composition_id:      str
    source_artifact_id:  str
    source_receipt_hash: str
    plan_id:             str
    plan_hash:           str

    width:    int
    height:   int
    fps:      int
    duration: int     # total seconds

    html:   str          # full HTML document
    assets: List[Asset]

    composition_hash: str    # sha256 of html + canonical(assets)
    authority: bool = False  # C2

    def __post_init__(self) -> None:
        if self.authority:
            raise ValueError("HTMLCompositionV1.authority must be False")


# ── Camera move → GSAP config ──────────────────────────────────────────────────

_CAMERA_GSAP: Dict[str, Dict[str, Any]] = {
    "slow_push_in":    {"scale": "1.08", "x": "0",    "y": "0",   "duration_factor": 1.0},
    "pull_back":       {"scale": "0.94", "x": "0",    "y": "0",   "duration_factor": 1.0},
    "handheld_micro":  {"scale": "1.00", "x": "4px",  "y": "3px", "duration_factor": 0.3},
    "orbit":           {"scale": "1.04", "x": "12px", "y": "0",   "duration_factor": 1.0},
    "drift":           {"scale": "1.02", "x": "6px",  "y": "4px", "duration_factor": 1.0},
    "static":          {"scale": "1.00", "x": "0",    "y": "0",   "duration_factor": 0.0},
}


def _camera_css(move: CameraMove, duration: int) -> str:
    cfg = _CAMERA_GSAP.get(move, _CAMERA_GSAP["drift"])
    factor = cfg["duration_factor"]
    dur = round(duration * factor, 1) if factor else 0
    if dur == 0:
        return ""
    return (
        f"transform: scale({cfg['scale']}) translate({cfg['x']}, {cfg['y']}); "
        f"transition: transform {dur}s ease-in-out;"
    )


# ── Shot → HTML block ──────────────────────────────────────────────────────────

def _shot_to_div(shot: Shot, start: int, z_index: int) -> str:
    cam_css   = _camera_css(shot.camera, shot.duration)
    visual_id = sha256_hex(shot.visual)[:8]

    overlay = ""
    if shot.text_overlay:
        overlay = f"""
        <div class="text-overlay" data-start="{start}" data-duration="{shot.duration}">
          <span class="overlay-text">{shot.text_overlay}</span>
        </div>"""

    fx_classes = " ".join(f"fx-{f}" for f in (shot.fx or []))

    return f"""
    <div class="shot shot-{shot.type} {fx_classes}"
         data-start="{start}"
         data-duration="{shot.duration}"
         data-camera="{shot.camera}"
         data-visual="{visual_id}"
         style="z-index:{z_index}; {cam_css}"
         title="{shot.visual}">
      <div class="shot-inner">
        <div class="visual-layer visual-{visual_id}"></div>
        <div class="particle-layer"></div>
        {overlay.strip()}
      </div>
    </div>"""


# ── Sound → HTML ───────────────────────────────────────────────────────────────

def _sound_to_html(sound, composition_id: str) -> str:
    if sound.music == "none":
        return ""
    return f"""
    <!-- Sound: {sound.music} | fx: {', '.join(sound.fx)} -->
    <!-- mix: {sound.mix_notes} -->
    <audio id="music-bed" data-start="0" loop preload="none"
           src="assets/{composition_id}/music.wav"></audio>"""


# ── Voice directive → meta comment ────────────────────────────────────────────

def _voice_to_comment(voice) -> str:
    return f"""
    <!--
    VOICE DIRECTIVE (for TTS prompt):
    STATE:       {voice.state}
    ENERGY:      {' → '.join(voice.energy_curve)}
    BREATH:      {voice.breath}
    TEMPO:       {voice.tempo}
    FIRST LINES: {voice.first_lines}
    MID SECTION: {voice.mid_section}
    FINAL LINE:  {voice.final_line}
    NOTES:       {voice.delivery_notes}
    -->"""


# ── Emotion curve → CSS class ──────────────────────────────────────────────────

def _emotion_to_body_class(curve: List[str]) -> str:
    return "emotion-" + "-".join(curve[:3])


# ── Full HTML document ─────────────────────────────────────────────────────────

_HTML_TEMPLATE = """\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>HELEN — {composition_id}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@300;400;500&display=swap" rel="stylesheet">
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js"></script>
<style>
/* HELEN Visual DNA — constitutional */
*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

:root {{
  --bg:          #050a1a;
  --accent:      #d4a843;
  --accent-dim:  #7a5c1e;
  --text-primary: rgba(220, 210, 190, 0.92);
  --text-dim:     rgba(180, 170, 155, 0.55);
  --particle:     rgba(212, 168, 67, 0.18);
  --w:            {width}px;
  --h:            {height}px;
}}

html, body {{
  width: var(--w); height: var(--h);
  overflow: hidden;
  background: var(--bg);
  font-family: 'Cormorant Garamond', Georgia, serif;
  color: var(--text-primary);
}}

.stage {{
  position: relative;
  width: var(--w); height: var(--h);
  overflow: hidden;
}}

/* Shots */
.shot {{
  position: absolute;
  inset: 0;
  opacity: 0;
  will-change: transform, opacity;
}}

.shot-inner {{
  position: relative;
  width: 100%; height: 100%;
}}

/* Visual layers — renderer fills these with AI-generated or procedural content */
.visual-layer {{
  position: absolute;
  inset: 0;
  background: var(--bg);
}}

/* Particle system */
.particle-layer {{
  position: absolute;
  inset: 0;
  pointer-events: none;
  overflow: hidden;
}}

.particle-layer::before,
.particle-layer::after {{
  content: '';
  position: absolute;
  width: 2px; height: 2px;
  border-radius: 50%;
  background: var(--particle);
  box-shadow:
    120px 240px 0 var(--particle), 340px 80px 0 var(--particle),
    560px 320px 0 var(--particle), 780px 160px 0 var(--particle),
    900px 480px 0 var(--particle), 1100px 220px 0 var(--particle),
    1400px 360px 0 var(--particle), 1680px 140px 0 var(--particle),
    200px 600px 0 var(--particle), 480px 750px 0 var(--particle),
    720px 820px 0 var(--particle), 1200px 680px 0 var(--particle);
  animation: drift-particles {particle_duration}s linear infinite;
}}
.particle-layer::after {{
  animation-delay: -{particle_delay}s;
  opacity: 0.6;
}}

@keyframes drift-particles {{
  from {{ transform: translateY(0) translateX(0); }}
  to   {{ transform: translateY(-60px) translateX(20px); }}
}}

/* Text overlays */
.text-overlay {{
  position: absolute;
  bottom: 12%;
  left: 50%;
  transform: translateX(-50%);
  opacity: 0;
  text-align: center;
  z-index: 100;
}}

.overlay-text {{
  display: block;
  font-size: 3.2rem;
  font-weight: 300;
  letter-spacing: 0.18em;
  color: var(--text-primary);
  text-shadow: 0 0 40px rgba(212, 168, 67, 0.3);
}}

/* Shot type modifiers */
.shot-close .visual-layer      {{ filter: blur(0px); }}
.shot-extreme_close .shot-inner {{ transform: scale(1.4); }}
.shot-wide .shot-inner          {{ transform: scale(1.0); }}
.shot-aerial .shot-inner        {{ transform: scale(0.85) translateY(-5%); }}

/* Emotion modifiers */
.emotion-calm .particle-layer      {{ opacity: 0.6; }}
.emotion-tension .particle-layer   {{ opacity: 1.0; animation-duration: 6s; }}
.emotion-release .particle-layer   {{ opacity: 0.4; animation-duration: 22s; }}
.emotion-silence .particle-layer   {{ opacity: 0.15; }}

/* FX classes */
.fx-particles .particle-layer      {{ opacity: 1.0; }}
.fx-breath                         {{ animation: subtle-pulse 4s ease-in-out infinite; }}
.fx-low_rumble .visual-layer       {{ filter: brightness(0.85) contrast(1.1); }}

@keyframes subtle-pulse {{
  0%, 100% {{ transform: scale(1.000); }}
  50%      {{ transform: scale(1.005); }}
}}

/* Vignette — always present */
.stage::after {{
  content: '';
  position: absolute;
  inset: 0;
  background: radial-gradient(
    ellipse at center,
    transparent 45%,
    rgba(5, 10, 26, 0.55) 75%,
    rgba(5, 10, 26, 0.88) 100%
  );
  pointer-events: none;
  z-index: 200;
}}

/* Receipt seal — bottom right, always */
.receipt-seal {{
  position: absolute;
  bottom: 1.5rem;
  right: 2rem;
  font-size: 0.65rem;
  letter-spacing: 0.12em;
  color: var(--text-dim);
  z-index: 300;
  opacity: 0;
  transition: opacity 1s ease;
}}
</style>
</head>
<body class="{body_class}">

{voice_comment}

<!-- Provenance -->
<!-- composition_id:      {composition_id} -->
<!-- source_artifact_id:  {source_artifact_id} -->
<!-- source_receipt_hash: {source_receipt_hash} -->
<!-- plan_id:             {plan_id} -->
<!-- plan_hash:           {plan_hash} -->
<!-- authority:           false -->

<script type="application/json" id="helen-script-data">
{script_json}
</script>

<div class="stage" id="stage">
  {shots_html}
  {sound_html}

  <div class="receipt-seal" id="receipt-seal">
    {source_receipt_hash_short} · authority:false
  </div>
</div>

<script>
// HELEN GSAP timeline — driven by data-start / data-duration attributes
(function() {{
  const tl = gsap.timeline({{ paused: true }});
  const shots = document.querySelectorAll('.shot');
  const overlays = document.querySelectorAll('.text-overlay');

  // Fade shots in/out per timing
  shots.forEach(el => {{
    const start    = parseFloat(el.dataset.start);
    const duration = parseFloat(el.dataset.duration);
    const camera   = el.dataset.camera || 'drift';

    tl.to(el, {{ opacity: 1, duration: 0.8, ease: "power2.inOut" }}, start);
    tl.to(el, {{ opacity: 0, duration: 0.6, ease: "power1.in" }}, start + duration - 0.6);
  }});

  // Text overlays
  overlays.forEach(el => {{
    const start    = parseFloat(el.dataset.start);
    const duration = parseFloat(el.dataset.duration);
    tl.to(el, {{ opacity: 1, y: "-8px", duration: 1.2, ease: "power2.out" }}, start + 0.4);
    tl.to(el, {{ opacity: 0, duration: 0.8, ease: "power1.in" }}, start + duration - 0.8);
  }});

  // Receipt seal fades in at end
  tl.to('#receipt-seal', {{ opacity: 1, duration: 2 }}, {total_duration} - 4);

  // Expose for renderer
  window.__helenTimeline = tl;
  window.__helenDuration = {total_duration};
  window.__helenFPS      = {fps};

  // Auto-play when renderer signals ready
  document.addEventListener('helen:render-start', () => tl.play());
  // HyperFrames hook
  if (window.__hyperframes) {{
    window.__hyperframes.onReady(() => tl.play());
  }} else {{
    tl.play();  // dev preview
  }}
}})();
</script>

</body>
</html>
"""


def director_to_html(
    plan:     DirectorPlanV1,
    artifact: ExecutionArtifactV1,
    width:    int = 1920,
    height:   int = 1080,
    fps:      int = 30,
) -> HTMLCompositionV1:
    """
    Deterministic: same plan + artifact → same HTML bytes (C1).
    Pure function. No ambient reads. No randomness.
    """
    composition_id = sha256_hex(f"{plan.plan_id}:{artifact.artifact_id}")[:16]

    # Build shot HTML with cumulative timing
    shots_html_parts = []
    cursor = 0
    for i, shot in enumerate(plan.shots):
        shots_html_parts.append(_shot_to_div(shot, start=cursor, z_index=10 + i))
        cursor += shot.duration

    total_duration = cursor
    shots_html     = "\n  ".join(shots_html_parts)
    sound_html     = _sound_to_html(plan.sound, composition_id)
    voice_comment  = _voice_to_comment(plan.voice)
    body_class     = _emotion_to_body_class(plan.emotion_curve)

    script_json = canonical_json({
        "content":   artifact.content,
        "tone":      artifact.tone,
        "persona":   artifact.persona,
        "plan_id":   plan.plan_id,
    })

    html = _HTML_TEMPLATE.format(
        composition_id=composition_id,
        source_artifact_id=artifact.artifact_id,
        source_receipt_hash=artifact.receipt_hash,
        source_receipt_hash_short=artifact.receipt_hash[7:23] + "…",
        plan_id=plan.plan_id,
        plan_hash=plan.plan_hash,
        width=width, height=height, fps=fps,
        total_duration=total_duration,
        particle_duration=total_duration + 8,
        particle_delay=round(total_duration / 2),
        body_class=body_class,
        shots_html=shots_html,
        sound_html=sound_html,
        voice_comment=voice_comment,
        script_json=script_json,
    )

    assets = [
        Asset(
            asset_id=sha256_hex(f"music:{composition_id}")[:12],
            type="audio",
            src=f"assets/{composition_id}/music.wav",
        ),
        Asset(
            asset_id=sha256_hex(f"voice:{composition_id}")[:12],
            type="audio",
            src=f"assets/{composition_id}/voice.wav",
        ),
    ]

    composition_hash = sha256_hex(
        html + canonical_json([dataclasses.asdict(a) for a in assets])
    )

    return HTMLCompositionV1(
        type=                "HTML_COMPOSITION_V1",
        composition_id=      composition_id,
        source_artifact_id=  artifact.artifact_id,
        source_receipt_hash= artifact.receipt_hash,
        plan_id=             plan.plan_id,
        plan_hash=           plan.plan_hash,
        width=width, height=height, fps=fps,
        duration=            total_duration,
        html=                html,
        assets=              assets,
        composition_hash=    "sha256:" + composition_hash,
        authority=           False,
    )
