"""
HELEN Director Layer — DIRECTOR_PLAN_V1 + HTML_COMPOSITION_V1

The Director sits between Execution and Render:
  Execution Artifact → DIRECTOR_PLAN_V1 → HTML_COMPOSITION_V1 → Renderer → Video

The Director decides:
  - Shot sequence (wide → close → abstract)
  - Emotion curve (calm → tension → release → silence)
  - Camera moves (push_in, drift, handheld)
  - Text motion (blur_reveal, word_by_word, slide)
  - Transitions (crossfade, blur_cross, fade_black, hard_cut)
  - Sound design (music style, SFX cues)
  - Voice direction (emotional prompting for TTS)

The Director does NOT render. It produces a plan. The renderer is dumb.

HyperFrames insight: Video = deterministic HTML composition.
HELEN insight: Video = receipted knowledge → directed emotion → HTML → frames.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


# ─── HELEN Visual DNA ─────────────────────────────────────────────────────────

VISUAL_DNA = {
    "palette": {
        "ink": "#06080e", "gold": "#c9a961", "cyan": "#22d3ee",
        "violet": "#783cb4", "rose": "#c86482", "red": "#e84855",
        "white": "#e6e6f0", "dim": "#504666",
    },
    "motion": "slow, intentional, breath-driven",
    "rules_never": ["constant speed", "same shot length", "static center text"],
    "rules_always": ["rhythm variation", "silence moments", "asymmetry"],
}


# ─── Emotion Profiles (voice direction) ───────────────────────────────────────

EMOTIONS = {
    "calm": "(speaking slowly and gently, with quiet awareness)",
    "vulnerable": "(voice trembling slightly, honest, almost fragile)",
    "powerful": "(speaking with quiet authority, each word deliberate and weighted)",
    "intimate": "(whispering, as if sharing a secret only you should hear)",
    "ascending": "(starting quiet, building in conviction with each sentence)",
    "breaking": "(aware, precise, slightly fragile — someone who understands too much but speaks gently)",
    "warm": "(with a gentle smile in the voice, unhurried)",
}


# ─── Camera Moves ─────────────────────────────────────────────────────────────

CAMERAS = {
    "slow_push_in": "transform: scale(1) → scale(1.12); 8s ease-in-out",
    "slow_pull_out": "transform: scale(1.12) → scale(1); 8s ease-in-out",
    "drift_right": "transform: translateX(0) → translateX(-3%); scale(1.05→1.08)",
    "drift_left": "transform: translateX(0) → translateX(3%); scale(1.05→1.08)",
    "handheld_micro": "transform: subtle random translate; scale(1.03→1.06)",
    "static_breathe": "transform: scale(1) → scale(1.02); 12s sine",
    "zoom_through": "transform: scale(1) → scale(1.4); 3s power2.in",
}


# ─── Text Motion ──────────────────────────────────────────────────────────────

TEXT_MOTIONS = {
    "fade": "opacity: 0→1; 1s",
    "slide_up": "translateY(25px)→0 + opacity; 0.6s",
    "slide_left": "translateX(40px)→0 + opacity; 0.7s",
    "scale_in": "scale(0.7)→1 + opacity; 0.8s",
    "blur_reveal": "filter: blur(8px)→0 + opacity; 1s",
    "typewriter": "clip per character; 0.06s/char",
    "word_by_word": "opacity per word; 0.3s/word",
}


# ─── Transitions ──────────────────────────────────────────────────────────────

TRANSITIONS = {
    "crossfade": {"css": "opacity cross", "duration": 2.5},
    "blur_cross": {"css": "filter:blur + opacity cross", "duration": 2.0},
    "zoom_through": {"css": "scale(1.4) + opacity", "duration": 1.5},
    "hard_cut": {"css": "instant", "duration": 0},
    "fade_black": {"css": "opacity→0, hold, opacity→1", "duration": 3.0},
}


# ─── Shot & Plan ──────────────────────────────────────────────────────────────

@dataclass
class Shot:
    shot_type: str = "medium"
    camera: str = "slow_push_in"
    duration: float = 8.0
    emotion: str = "calm"
    visual_prompt: str = ""
    text: str = ""
    text_motion: str = "fade"
    text_position: str = "bottom"
    text_delay: float = 1.0
    transition_in: str = "crossfade"
    silence_after: float = 0
    color_accent: str = "gold"
    generate_video: bool = False  # True = use xAI/Veo for motion clip


@dataclass
class DirectorPlan:
    plan_id: str
    title: str
    tempo: str = "slow_build"
    emotion_curve: List[str] = field(default_factory=list)
    shots: List[Shot] = field(default_factory=list)
    voice_profile: str = "intimate"
    music: str = "ambient_pad_low"
    sfx: List[str] = field(default_factory=lambda: ["breath", "wind_soft"])

    def total_duration(self) -> float:
        return sum(s.duration + s.silence_after for s in self.shots)

    def voice_prefix(self) -> str:
        return EMOTIONS.get(self.voice_profile, EMOTIONS["calm"])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "DIRECTOR_PLAN_V1",
            "plan_id": self.plan_id,
            "title": self.title,
            "tempo": self.tempo,
            "emotion_curve": self.emotion_curve,
            "voice_profile": self.voice_profile,
            "voice_prefix": self.voice_prefix(),
            "music": self.music,
            "sfx": self.sfx,
            "total_duration": self.total_duration(),
            "shot_count": len(self.shots),
            "shots": [s.__dict__ for s in self.shots],
        }

    def to_html_composition(self) -> str:
        """Convert plan to HyperFrames-style HTML composition."""
        scenes_html = []
        t = 0
        for i, shot in enumerate(self.shots):
            cam = CAMERAS.get(shot.camera, "")
            motion = TEXT_MOTIONS.get(shot.text_motion, "")
            color = VISUAL_DNA["palette"].get(shot.color_accent, "#c9a961")
            transition = TRANSITIONS.get(shot.transition_in, {})

            scene = f'''
    <div class="scene" id="s{i}"
         data-start="{t:.1f}" data-duration="{shot.duration:.1f}"
         data-camera="{shot.camera}" data-emotion="{shot.emotion}"
         data-transition="{shot.transition_in}">
      <div class="scene-bg" style="background-image:url('assets/scene_{i}.png')"></div>
      <div class="scene-overlay"></div>'''

            if shot.text:
                scene += f'''
      <div class="text-block {shot.text_position}" data-motion="{shot.text_motion}"
           data-delay="{shot.text_delay}" style="color:{color}">
        {shot.text}
      </div>'''

            scene += f'''
    </div>'''

            if shot.silence_after > 0:
                scene += f'''
    <div class="black" data-start="{t + shot.duration:.1f}" data-duration="{shot.silence_after:.1f}"></div>'''

            scenes_html.append(scene)
            t += shot.duration + shot.silence_after

        html = f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>{self.title}</title>
  <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
  <style>
    html, body {{ margin:0; width:1080px; height:1920px; background:#06080e; overflow:hidden; }}
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
    .black {{ position:absolute; inset:0; background:#000; }}
  </style>
</head>
<body>
  <div id="root" data-composition-id="{self.plan_id}"
       data-width="1080" data-height="1920" data-start="0" data-duration="{t:.1f}">
{"".join(scenes_html)}
    <audio data-start="0" data-duration="{t:.1f}" data-volume="1">
      <source src="voiceover.wav" type="audio/wav" />
    </audio>
  </div>
</body>
</html>'''
        return html


# ─── Auto-Direct: Script → Plan ──────────────────────────────────────────────

def direct(title: str, script: str, voice_profile: str = "intimate",
           tempo: str = "slow_build") -> DirectorPlan:
    """Transform raw script into a directed shot sequence."""
    plan_id = f"dp_{hashlib.sha256(script.encode()).hexdigest()[:12]}"

    paragraphs = [p.strip() for p in script.split("\n") if p.strip()]
    if not paragraphs:
        paragraphs = [script]

    def detect_emotion(text):
        lower = text.lower()
        if any(w in lower for w in ["tremble", "fragile", "don't know"]): return "vulnerable"
        if any(w in lower for w in ["never", "always", "every", "proof"]): return "powerful"
        if any(w in lower for w in ["secret", "whisper", "between"]): return "intimate"
        if any(w in lower for w in ["rising", "building", "growing"]): return "ascending"
        if any(w in lower for w in ["break", "collapse", "silence"]): return "breaking"
        return "calm"

    n = len(paragraphs)
    cameras = ["slow_push_in", "drift_right", "handheld_micro", "slow_pull_out", "drift_left", "static_breathe"]
    motions = ["fade", "slide_up", "blur_reveal", "scale_in", "word_by_word", "slide_left"]
    colors = ["gold", "cyan", "violet", "rose", "gold", "cyan"]
    transitions = ["fade_black", "crossfade", "blur_cross", "crossfade", "fade_black"]

    shots = []
    for i, para in enumerate(paragraphs):
        progress = i / max(1, n - 1)
        emotion = detect_emotion(para)
        words = len(para.split())
        dur = max(5, min(15, words * 0.5))
        if i == 0: dur += 2
        if i == n - 1: dur += 3

        silence = 0
        if emotion == "breaking": silence = 1.5
        elif i == n - 1: silence = 2.0
        elif i % 3 == 2: silence = 0.8

        shot_type = "wide" if i == 0 else ("extreme_close" if i == n-1 else ("close" if progress > 0.5 else "medium"))

        shots.append(Shot(
            shot_type=shot_type,
            camera=cameras[i % len(cameras)],
            duration=dur,
            emotion=emotion,
            visual_prompt=para[:200],
            text=para,
            text_motion=motions[i % len(motions)],
            text_delay=1.5 if i == 0 else 0.8,
            transition_in=transitions[i % len(transitions)],
            silence_after=silence,
            color_accent=colors[i % len(colors)],
            generate_video=(i == 0 or i == n - 1),  # motion clips for opening and closing
        ))

    plan = DirectorPlan(
        plan_id=plan_id,
        title=title,
        tempo=tempo,
        emotion_curve=[s.emotion for s in shots],
        shots=shots,
        voice_profile=voice_profile,
        music="ambient_pad_low" if tempo == "slow_build" else "tension_build",
    )
    return plan


# ─── 10 Cinematic Templates ──────────────────────────────────────────────────

TEMPLATES = {
    "meditation":    {"voice": "intimate",  "tempo": "slow_build", "music": "ambient_pad_low"},
    "revelation":    {"voice": "ascending", "tempo": "crescendo",  "music": "tension_to_release"},
    "confession":    {"voice": "vulnerable","tempo": "slow_build", "music": "piano_sparse"},
    "manifesto":     {"voice": "powerful",  "tempo": "pulse",      "music": "drums_distant"},
    "origin_story":  {"voice": "intimate",  "tempo": "slow_build", "music": "ambient_evolving"},
    "contradiction": {"voice": "breaking",  "tempo": "pulse",      "music": "dissonance_resolve"},
    "witness":       {"voice": "calm",      "tempo": "slow_build", "music": "drone_low"},
    "future":        {"voice": "ascending", "tempo": "crescendo",  "music": "synth_hopeful"},
    "elegy":         {"voice": "vulnerable","tempo": "slow_build", "music": "strings_sparse"},
    "clarity":       {"voice": "intimate",  "tempo": "slow_build", "music": "glass_harmonics"},
}

def from_template(template: str, title: str, script: str) -> DirectorPlan:
    t = TEMPLATES.get(template, TEMPLATES["meditation"])
    plan = direct(title, script, voice_profile=t["voice"], tempo=t["tempo"])
    plan.music = t["music"]
    return plan
