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
from .director import DirectorPlanV1, Shot
from .models import ExecutionArtifactV1
from .presets import (
    camera_gsap, transition_gsap, text_gsap,
    emotion_filter, receipt_seal_gsap,
    wrap_words, wrap_chars, load_presets_js,
)


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


# camera_gsap, transition_gsap, text_gsap are imported from presets.py


# ── Shot → HTML block ──────────────────────────────────────────────────────────

def _shot_to_div(shot: Shot, start: int, z_index: int) -> tuple:
    """Returns (html_div, gsap_js_block) for the shot."""
    # Compat: support both Shot field naming conventions
    visual    = getattr(shot, "visual", None) or getattr(shot, "visual_prompt", "")
    text_ovly = getattr(shot, "text_overlay", None) or getattr(shot, "text", None) or ""
    duration  = float(getattr(shot, "duration", 8))
    shot_type = getattr(shot, "type", None) or getattr(shot, "shot_type", "medium")
    emotion   = getattr(shot, "emotion", "calm")
    text_motion = getattr(shot, "text_motion", "fade")
    text_delay  = float(getattr(shot, "text_delay", 1.0))
    transition  = getattr(shot, "transition_in", "crossfade")

    visual_id = sha256_hex(visual)[:8]
    shot_id   = f"shot_{z_index}"
    em_filter = emotion_filter(emotion)

    # Text: wrap for word-by-word or typewriter if needed
    text_html = text_ovly
    if text_motion == "word_by_word":
        text_html = wrap_words(text_ovly)
    elif text_motion == "typewriter":
        text_html = wrap_chars(text_ovly)

    overlay = ""
    if text_html.strip():
        overlay = f"""
        <div class="text-overlay" id="txt_{shot_id}"
             data-start="{start}" data-duration="{int(duration)}">
          <span class="overlay-text">{text_html}</span>
        </div>"""

    div = f"""
    <div class="shot shot-{shot_type}" id="{shot_id}"
         data-start="{start}"
         data-duration="{int(duration)}"
         data-camera="{shot.camera}"
         data-visual="{visual_id}"
         data-emotion="{emotion}"
         data-transition="{transition}"
         style="z-index:{z_index};"
         title="{visual[:80]}">
      <div class="shot-inner" id="inner_{shot_id}">
        <div class="visual-layer visual-{visual_id}"
             style="filter: {em_filter};"></div>
        <div class="particle-layer"></div>
        {overlay.strip()}
      </div>
    </div>"""

    # GSAP JS for this shot
    js = camera_gsap(shot.camera, el=f"document.getElementById('inner_{shot_id}')",
                     duration=duration, start=start)
    if text_html.strip():
        js += text_gsap(text_motion,
                        el=f"document.getElementById('txt_{shot_id}')",
                        delay=start + text_delay,
                        uid=shot_id)

    return div, js


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
// ── HELEN Cinematic Presets (inlined) ─────────────────────────────────────────
{presets_js}
</script>
<script>
// HELEN GSAP master timeline — seekable by renderer
(function() {{
  // ── Master timeline (single seekable surface) ─────────────────────────────
  const masterTL = gsap.timeline({{ paused: true }});
  window.__timelines = [masterTL];
  window.__seek      = (t) => masterTL.seek(t, false);

  // ── Structural: shot visibility on timeline ───────────────────────────────
  gsap.set('.shot', {{ opacity: 0 }});
  document.querySelectorAll('.shot').forEach(el => {{
    const t0  = parseFloat(el.dataset.start);
    const dur = parseFloat(el.dataset.duration);
    masterTL.to(el, {{ opacity: 1, duration: 0.7, ease: 'power2.inOut' }}, t0);
    masterTL.to(el, {{ opacity: 0, duration: 0.5, ease: 'power1.in'    }}, t0 + dur - 0.5);
  }});

  // ── Per-shot camera + text + transitions ──────────────────────────────────
  {shots_gsap_js}

  // ── Receipt seal ──────────────────────────────────────────────────────────
  gsap.set('#receipt-seal', {{ opacity: 0, y: 8 }});
  {receipt_seal_js}

  // ── Renderer contract ─────────────────────────────────────────────────────
  window.__ready    = true;      // renderer waits for this
  window.__duration = {total_duration};
  window.__fps      = {fps};

  // ── Dev preview: auto-play ────────────────────────────────────────────────
  document.addEventListener('helen:render-start', () => masterTL.play());
  if (document.readyState !== 'loading') masterTL.play();
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
    shot_divs, shot_js_blocks = [], []
    cursor = 0.0
    for i, shot in enumerate(plan.shots):
        dur     = float(getattr(shot, "duration", 8))
        silence = float(getattr(shot, "silence_after", 0))
        div, js = _shot_to_div(shot, start=int(cursor), z_index=10 + i)
        shot_divs.append(div)
        shot_js_blocks.append(js)

        # Transition to next shot
        if i < len(plan.shots) - 1:
            trans_name   = getattr(shot, "transition_in", "crossfade")
            trans_dur    = 1.8
            trans_start  = cursor + dur - trans_dur   # overlap start (absolute)
            shot_id_curr = f"shot_{10 + i}"
            shot_id_next = f"shot_{10 + i + 1}"
            shot_js_blocks.append(
                transition_gsap(trans_name,
                                el_out=f"document.getElementById('{shot_id_curr}')",
                                el_in=f"document.getElementById('{shot_id_next}')",
                                duration=trans_dur,
                                start=trans_start)
            )

        cursor += dur + silence

    total_duration   = cursor
    shots_html       = "\n  ".join(shot_divs)
    shots_gsap_js    = "\n      ".join(shot_js_blocks)
    receipt_seal_js  = receipt_seal_gsap(total_duration)
    sound_html       = _sound_to_html(plan.sound, composition_id)
    voice_comment    = _voice_to_comment(plan.voice)
    body_class       = _emotion_to_body_class(plan.emotion_curve)
    presets_js       = load_presets_js()

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
        total_duration=int(total_duration),
        particle_duration=int(total_duration) + 8,
        particle_delay=round(total_duration / 2),
        body_class=body_class,
        shots_html=shots_html,
        shots_gsap_js=shots_gsap_js,
        receipt_seal_js=receipt_seal_js,
        sound_html=sound_html,
        voice_comment=voice_comment,
        script_json=script_json,
        presets_js=presets_js,
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
