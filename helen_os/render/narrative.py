"""
HELEN Narrative Layer — Timeline IR Compiler

The semantic layer between script meaning and render bytes.

Pipeline:
  Script → NarrativeArc → TimelineIRV1 → (compile) → MontagePlanV1
                                                     → DirectorPlan shots

Principle: FFmpeg and the GSAP renderer are backends.
           The timeline is the truth layer.

Key types:
  NarrativeBeat       — one beat: name, emotion, camera, transition, duration ratio
  NARRATIVE_ARCS      — library of named arcs (four arcs, covering key story shapes)
  TimelineSegment     — one segment on the IR: typed, timed, hashed
  TimelineIRV1        — the full IR: segments + provenance + hash
  map_script_to_arc() — script + arc → TimelineIRV1
  compile_to_montage()— TimelineIRV1 → MontagePlanV1
  compile_to_shots()  — TimelineIRV1 → List[dict] (Director-compatible shot dicts)

Invariants:
  IR1: authority=False on every TimelineIRV1
  IR2: timeline_hash = sha256(canonical(segments))
  IR3: segment durations sum to total_duration (within 0.01s)
  IR4: segment emotions are valid HELEN emotion labels
  IR5: same script + arc + duration → same timeline_hash
  IR6: compile_to_montage() produces authority=False MontagePlanV1
"""
from __future__ import annotations

import hashlib
import json
import re
import textwrap
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from .contracts import canonical_json, sha256_hex
from .montage import (
    AudioSpec, ClipSpec, MontagePlanV1,
    RHYTHM_PRESETS, TRANSITIONS,
    rhythm_from_emotion,
)


# ── Valid emotion labels ───────────────────────────────────────────────────────

VALID_EMOTIONS = frozenset({
    "calm", "ascending", "tension", "powerful",
    "intimate", "vulnerable", "breaking", "warm", "release",
})


# ── Narrative beat ─────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class NarrativeBeat:
    name:             str
    duration_ratio:   float    # fraction of total_duration for this beat
    emotion:          str      # must be in VALID_EMOTIONS
    camera_move:      str      # from presets._CAMERA_FN keys
    transition_out:   str      # from TRANSITIONS keys
    text_motion:      str = "fade"


# ── Arc library ────────────────────────────────────────────────────────────────

NARRATIVE_ARCS: Dict[str, List[NarrativeBeat]] = {

    "three_act": [
        NarrativeBeat("setup",     0.20, "calm",       "slow_push_in",   "fade"),
        NarrativeBeat("rising",    0.25, "ascending",  "drift_right",    "dissolve"),
        NarrativeBeat("tension",   0.20, "tension",    "handheld_micro", "hard_cut"),
        NarrativeBeat("peak",      0.10, "powerful",   "zoom_through",   "zoom_through"),
        NarrativeBeat("release",   0.15, "calm",       "slow_pull_out",  "fade",         "slide_up"),
        NarrativeBeat("resolution",0.10, "warm",       "static_breathe", "dissolve"),
    ],

    "meditation": [
        NarrativeBeat("arrival",   0.25, "calm",       "slow_push_in",   "fade"),
        NarrativeBeat("deepening", 0.30, "intimate",   "static_breathe", "dissolve",     "blur_reveal"),
        NarrativeBeat("insight",   0.25, "ascending",  "drift_right",    "fade",         "word_by_word"),
        NarrativeBeat("return",    0.20, "warm",       "slow_pull_out",  "fade"),
    ],

    "revelation": [
        NarrativeBeat("silence",   0.20, "calm",       "static_breathe", "fade"),
        NarrativeBeat("rupture",   0.15, "breaking",   "zoom_through",   "hard_cut",     "scale_in"),
        NarrativeBeat("reframe",   0.30, "powerful",   "slow_push_in",   "dissolve"),
        NarrativeBeat("resolve",   0.35, "ascending",  "drift_right",    "fade",         "slide_up"),
    ],

    "testimony": [
        NarrativeBeat("context",   0.20, "calm",       "static_breathe", "fade"),
        NarrativeBeat("wound",     0.25, "tension",    "handheld_micro", "hard_cut"),
        NarrativeBeat("turn",      0.20, "breaking",   "zoom_through",   "zoom_through", "typewriter"),
        NarrativeBeat("evidence",  0.25, "powerful",   "slow_push_in",   "dissolve"),
        NarrativeBeat("verdict",   0.10, "warm",       "slow_pull_out",  "fade",         "fade"),
    ],

    "manifesto": [
        NarrativeBeat("declaration",0.25, "powerful",  "slow_push_in",   "fade",         "scale_in"),
        NarrativeBeat("evidence",   0.30, "ascending", "drift_right",    "dissolve"),
        NarrativeBeat("challenge",  0.20, "tension",   "handheld_micro", "hard_cut"),
        NarrativeBeat("call",       0.25, "powerful",  "zoom_through",   "fade",         "word_by_word"),
    ],
}

# Tone-to-arc mapping (for auto-selecting arc from artifact tone)
TONE_ARC: Dict[str, str] = {
    "calm":        "meditation",
    "reflective":  "meditation",
    "serious":     "three_act",
    "precise":     "revelation",
    "warm":        "meditation",
    "vulnerable":  "testimony",
    "powerful":    "manifesto",
    "urgent":      "three_act",
}


def arc_from_tone(tone: str) -> str:
    return TONE_ARC.get(tone, "three_act")


# ── Timeline segment ───────────────────────────────────────────────────────────

@dataclass(frozen=True)
class TimelineSegment:
    segment_id:     str
    beat_name:      str       # narrative beat name
    start:          float     # absolute start in output (seconds)
    end:            float     # absolute end in output
    duration:       float
    emotion:        str
    camera_move:    str
    transition_out: str
    text_motion:    str
    text:           str       # script text assigned to this segment
    clip_src:       str       # path to clip file ("" = not yet rendered)


# ── TimelineIRV1 ───────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class TimelineIRV1:
    """
    Intermediate Representation — the truth layer between meaning and render.

    Compiles to:
      - MontagePlanV1    via compile_to_montage()
      - Shot list        via compile_to_shots()

    Invariants: IR1-IR6 (see module docstring).
    """
    type:                str   # always "TIMELINE_IR_V1"
    timeline_id:         str
    source_artifact_id:  str
    source_receipt_hash: str
    arc_name:            str
    total_duration:      float
    segments:            List[TimelineSegment]
    timeline_hash:       str
    authority:           bool  = False

    def __post_init__(self) -> None:
        if self.authority:
            raise ValueError("TimelineIRV1.authority must be False")

    def dominant_emotion(self) -> str:
        """Emotion of the longest segment."""
        if not self.segments:
            return "calm"
        return max(self.segments, key=lambda s: s.duration).emotion

    def emotion_curve(self) -> List[str]:
        return [s.emotion for s in self.segments]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type":                self.type,
            "timeline_id":         self.timeline_id,
            "source_artifact_id":  self.source_artifact_id,
            "source_receipt_hash": self.source_receipt_hash,
            "arc_name":            self.arc_name,
            "total_duration":      self.total_duration,
            "segments": [
                {
                    "segment_id":     s.segment_id,
                    "beat_name":      s.beat_name,
                    "start":          s.start,
                    "end":            s.end,
                    "duration":       s.duration,
                    "emotion":        s.emotion,
                    "camera_move":    s.camera_move,
                    "transition_out": s.transition_out,
                    "text_motion":    s.text_motion,
                    "text":           s.text,
                    "clip_src":       s.clip_src,
                }
                for s in self.segments
            ],
            "timeline_hash": self.timeline_hash,
            "authority":     False,
        }


# ── Script → text segments ────────────────────────────────────────────────────

def _split_script(script: str, beat_ratios: List[float]) -> List[str]:
    """
    Split a script into N text chunks proportional to beat_ratios.
    Tries to split at sentence boundaries; falls back to word boundaries.
    """
    sentences = re.split(r'(?<=[.!?])\s+', script.strip())
    if not sentences:
        return [""] * len(beat_ratios)

    n = len(beat_ratios)
    total = sum(beat_ratios)
    normalised = [r / total for r in beat_ratios]

    words  = script.split()
    chunks: List[str] = []
    cursor = 0
    for i, ratio in enumerate(normalised):
        if i == n - 1:
            chunks.append(" ".join(words[cursor:]))
        else:
            count  = max(1, round(len(words) * ratio))
            chunks.append(" ".join(words[cursor:cursor + count]))
            cursor += count
    return chunks


# ── Timeline hash ─────────────────────────────────────────────────────────────

def _segments_hash(segments: List[TimelineSegment]) -> str:
    payload = canonical_json([
        {
            "segment_id":     s.segment_id,
            "start":          s.start,
            "end":            s.end,
            "duration":       s.duration,
            "emotion":        s.emotion,
            "camera_move":    s.camera_move,
            "transition_out": s.transition_out,
            "text":           s.text,
        }
        for s in segments
    ])
    return "sha256:" + hashlib.sha256(payload.encode()).hexdigest()


# ── map_script_to_arc ─────────────────────────────────────────────────────────

def map_script_to_arc(
    script:               str,
    arc_name:             str = "three_act",
    total_duration:       float = 30.0,
    source_artifact_id:   str = "",
    source_receipt_hash:  str = "sha256:" + "0" * 64,
    clip_srcs:            Optional[List[str]] = None,
) -> TimelineIRV1:
    """
    Map a script to a TimelineIRV1 using the named narrative arc.

    Deterministic: same (script, arc_name, total_duration) → same timeline_hash.
    No LLM calls. No randomness.

    Args:
        script:              the text to distribute across beats
        arc_name:            key in NARRATIVE_ARCS
        total_duration:      total video duration in seconds
        source_artifact_id:  ExecutionArtifact.artifact_id for provenance
        source_receipt_hash: ExecutionArtifact.receipt_hash for provenance
        clip_srcs:           optional list of clip paths (one per beat; padded/truncated)
    """
    beats = NARRATIVE_ARCS.get(arc_name, NARRATIVE_ARCS["three_act"])
    ratios = [b.duration_ratio for b in beats]

    # Normalise ratios (they should already sum to ~1 but defend against drift)
    total_ratio = sum(ratios)
    normalised  = [r / total_ratio for r in ratios]

    text_chunks = _split_script(script, normalised)
    srcs        = clip_srcs or []

    segments: List[TimelineSegment] = []
    cursor = 0.0
    for i, beat in enumerate(beats):
        dur = round(total_duration * normalised[i], 4)
        segments.append(TimelineSegment(
            segment_id=     f"{arc_name}_{beat.name}_{i}",
            beat_name=       beat.name,
            start=           round(cursor, 4),
            end=             round(cursor + dur, 4),
            duration=        dur,
            emotion=         beat.emotion,
            camera_move=     beat.camera_move,
            transition_out=  beat.transition_out,
            text_motion=     beat.text_motion,
            text=            text_chunks[i] if i < len(text_chunks) else "",
            clip_src=        srcs[i] if i < len(srcs) else "",
        ))
        cursor += dur

    # Deterministic ID: hash of inputs
    timeline_id = "tl_" + sha256_hex(
        f"{arc_name}:{total_duration}:{script[:200]}"
    )[:12]

    tl_hash = _segments_hash(segments)

    return TimelineIRV1(
        type=                "TIMELINE_IR_V1",
        timeline_id=         timeline_id,
        source_artifact_id=  source_artifact_id,
        source_receipt_hash= source_receipt_hash,
        arc_name=            arc_name,
        total_duration=      round(cursor, 4),
        segments=            segments,
        timeline_hash=       tl_hash,
        authority=           False,
    )


# ── Compilers ─────────────────────────────────────────────────────────────────

def compile_to_montage(
    timeline:         TimelineIRV1,
    voiceover:        str = "",
    music:            str = "",
    music_volume:     float = 0.15,
) -> MontagePlanV1:
    """
    Compile a TimelineIRV1 → MontagePlanV1.

    Each segment becomes a ClipSpec.  Rhythm is inferred from the dominant emotion.
    Clip durations come from the solved timeline (not from the rhythm preset pattern).
    """
    clips = [
        ClipSpec(
            src=            seg.clip_src or f"placeholder_{seg.segment_id}.mp4",
            start=          0.0,
            duration=       seg.duration,
            transition_out= seg.transition_out,
            label=          seg.beat_name,
        )
        for seg in timeline.segments
    ]

    rhythm = rhythm_from_emotion(timeline.dominant_emotion())

    return MontagePlanV1(
        plan_id=        "mp_from_" + timeline.timeline_id,
        duration_target=timeline.total_duration,
        clips=          clips,
        audio=          AudioSpec(
            voiceover=    voiceover,
            music=        music,
            music_volume= music_volume,
        ),
        rhythm=         rhythm,
        authority=      False,
    )


def compile_to_shots(timeline: TimelineIRV1) -> List[Dict[str, Any]]:
    """
    Compile a TimelineIRV1 → list of Shot-compatible dicts for DirectorPlan.

    Each dict has keys matching DirectorPlan.Shot fields.
    """
    return [
        {
            "shot_type":     "medium",
            "visual_prompt": f"{seg.emotion} — {seg.beat_name}: {seg.text[:80]}",
            "text":          seg.text,
            "emotion":       seg.emotion,
            "camera":        seg.camera_move,
            "duration":      seg.duration,
            "text_motion":   seg.text_motion,
            "text_delay":    1.0,
            "silence_after": 0.0,
            "transition_in": seg.transition_out,
            "fx":            [],
            "voice_note":    "",
        }
        for seg in timeline.segments
    ]


# ── Emotion-aware transition override ─────────────────────────────────────────

def emotion_transition_override(emotion: str) -> str:
    """
    Override default transition based on detected emotion.
    Used when auto-editing without a fixed arc.
    """
    _MAP = {
        "tension":    "hard_cut",
        "breaking":   "zoom_through",
        "powerful":   "circleopen",
        "ascending":  "dissolve",
        "calm":       "fade",
        "intimate":   "fade",
        "vulnerable": "dissolve",
        "warm":       "fade",
        "release":    "dissolve",
    }
    return _MAP.get(emotion, "fade")
