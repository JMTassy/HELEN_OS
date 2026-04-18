"""
HELEN Render — Cinematic motion presets (Python side).

Python functions emit calls to helenCamera / helenText / helenTransition
JS objects (defined in oracle_town/.../presets/helen-presets.js and inlined
into every composition HTML).

All calls target a GSAP master timeline `masterTL` that lives in the
composition's <script> block.  The renderer seeks masterTL per-frame:
  window.__seek(t)  →  masterTL.seek(t, false)

Invariant: same arguments → same JS string (deterministic).
"""
from __future__ import annotations

from pathlib import Path
from typing import Optional


# ── JS preset source (inlined into every composition) ─────────────────────────

_PRESETS_JS_PATH = (
    Path(__file__).parent.parent.parent
    / "oracle_town/skills/video/hyperframes/presets/helen-presets.js"
)


def load_presets_js() -> str:
    """Read helen-presets.js for inline embedding in composition HTML."""
    try:
        return _PRESETS_JS_PATH.read_text(encoding="utf-8")
    except FileNotFoundError:
        # Fallback: minimal stubs so composition doesn't crash
        return (
            "const helenCamera = { staticBreathe: (tl,el,dur,t0) => "
            "tl.to(el,{scale:1.02,duration:6,yoyo:true,repeat:-1},t0) };\n"
            "const helenText = { fade: (tl,el,t0) => tl.from(el,{opacity:0,duration:1.2},t0) };\n"
            "const helenTransition = { crossfade: (tl,o,i,d,t0) => "
            "{ tl.to(o,{opacity:0,duration:d},t0); tl.from(i,{opacity:0,duration:d},t0); } };\n"
        )


# ── Camera move calls ──────────────────────────────────────────────────────────

_CAMERA_FN = {
    "slow_push_in":   "helenCamera.slowPushIn",
    "slow_pull_out":  "helenCamera.slowPullOut",
    "drift_right":    "helenCamera.driftRight",
    "drift_left":     "helenCamera.driftLeft",
    "handheld_micro": "helenCamera.handheldMicro",
    "static_breathe": "helenCamera.staticBreathe",
    "zoom_through":   "helenCamera.zoomThrough",
    "orbit":          "helenCamera.orbit",
}


def camera_gsap(move: str, el: str, duration: float, start: float) -> str:
    fn = _CAMERA_FN.get(move, "helenCamera.staticBreathe")
    return f"{fn}(masterTL, {el}, {round(duration, 2)}, {round(start, 2)});"


# ── Transition calls ───────────────────────────────────────────────────────────

_TRANSITION_FN = {
    "crossfade":   "helenTransition.crossfade",
    "blur_cross":  "helenTransition.blurCross",
    "fade_black":  "helenTransition.fadeBlack",
    "zoom_through":"helenTransition.zoomThrough",
    "hard_cut":    "helenTransition.hardCut",
}


def transition_gsap(
    name: str,
    el_out: str,
    el_in: str,
    duration: float,
    start: float = 0.0,
) -> str:
    fn = _TRANSITION_FN.get(name, "helenTransition.crossfade")
    return (
        f"{fn}(masterTL, {el_out}, {el_in}, "
        f"{round(duration, 2)}, {round(start, 2)});"
    )


# ── Text motion calls ──────────────────────────────────────────────────────────

_TEXT_FN = {
    "fade":        "helenText.fade",
    "slide_up":    "helenText.slideUp",
    "slide_left":  "helenText.slideLeft",
    "scale_in":    "helenText.scaleIn",
    "blur_reveal": "helenText.blurReveal",
    "word_by_word":"helenText.wordByWord",
    "typewriter":  "helenText.typewriter",
}


def text_gsap(motion: str, el: str, delay: float, uid: str = "0") -> str:
    fn = _TEXT_FN.get(motion, "helenText.fade")
    return f"{fn}(masterTL, {el}, {round(delay, 2)});"


# ── Word/char splitter (Python HTML generation) ────────────────────────────────

def wrap_words(text: str) -> str:
    """Wrap each word in <span class='word'> for wordByWord animation."""
    return " ".join(f"<span class='word'>{w}</span>" for w in text.split())


def wrap_chars(text: str) -> str:
    """Wrap each char in <span class='char'> for typewriter animation."""
    return "".join(
        f"<span class='char'>{c}</span>" if c != " " else " "
        for c in text
    )


# ── Emotion → CSS filter ───────────────────────────────────────────────────────

_EMOTION_FILTER = {
    "calm":       "brightness(1.0) saturate(1.0)",
    "vulnerable": "brightness(0.88) saturate(0.8) sepia(0.15)",
    "powerful":   "brightness(1.05) contrast(1.1) saturate(1.2)",
    "intimate":   "brightness(0.82) saturate(0.7) blur(0px)",
    "ascending":  "brightness(1.08) saturate(1.15)",
    "breaking":   "brightness(0.75) saturate(0.6) contrast(1.15)",
    "warm":       "brightness(1.02) sepia(0.12) saturate(1.1)",
}


def emotion_filter(emotion: str) -> str:
    return _EMOTION_FILTER.get(emotion, _EMOTION_FILTER["calm"])


# ── Receipt seal ───────────────────────────────────────────────────────────────

def receipt_seal_gsap(total_duration: float) -> str:
    t0 = round(max(0.0, total_duration - 4.5), 2)
    return (
        f"masterTL.to('#receipt-seal', "
        f"{{ opacity: 1, y: 0, duration: 2.5, ease: 'power2.out' }}, {t0});"
    )
