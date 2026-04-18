"""
HELEN Montage Engine — Timeline Compiler v3

V3 upgrades over naive linear assembler:
  - Timeline solver: precise per-clip start/end accounting for transition overlaps
  - Compiled filter graph: xfade offsets from solved timeline (not ad-hoc loops)
  - Rhythm presets: duration patterns, not just transition lists
  - Audio-sync: voice + music fade anchored to solved timeline
  - Emotion → rhythm mapping
  - Stronger receipt: timeline_hash + audio_hash + per-clip hashes

Determinism law: same MontagePlanV1 → same filter graph → same video bytes.
Authority law: authority=False on every plan and receipt — no exceptions.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


# ── Helpers ────────────────────────────────────────────────────────────────────

def _sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return "sha256:" + h.hexdigest()


def _canonical(data: Any) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"))


def _now_utc() -> str:
    import datetime
    return datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "Z")


def _probe_duration(path: str) -> float:
    try:
        r = subprocess.run(
            ["ffprobe", "-i", path, "-show_entries", "format=duration",
             "-v", "quiet", "-of", "csv=p=0"],
            capture_output=True, text=True, timeout=10,
        )
        return float(r.stdout.strip())
    except Exception:
        return 8.0


# ── Transitions ────────────────────────────────────────────────────────────────

TRANSITIONS: Dict[str, Dict[str, Any]] = {
    "fade":        {"ffmpeg": "fade",        "duration": 1.0},
    "dissolve":    {"ffmpeg": "dissolve",    "duration": 1.5},
    "slideleft":   {"ffmpeg": "slideleft",   "duration": 1.0},
    "slideright":  {"ffmpeg": "slideright",  "duration": 1.0},
    "slideup":     {"ffmpeg": "slideup",     "duration": 0.8},
    "circleopen":  {"ffmpeg": "circleopen",  "duration": 1.0},
    "circleclose": {"ffmpeg": "circleclose", "duration": 1.0},
    "wipeleft":    {"ffmpeg": "wipeleft",    "duration": 0.8},
    "wiperight":   {"ffmpeg": "wiperight",   "duration": 0.8},
    "radial":      {"ffmpeg": "radial",      "duration": 1.2},
    "smoothleft":  {"ffmpeg": "smoothleft",  "duration": 1.0},
    "smoothright":  {"ffmpeg": "smoothright", "duration": 1.0},
    "zoom_through": {"ffmpeg": "dissolve",   "duration": 1.2},   # visual zoom from camera preset
    "hard_cut":     {"ffmpeg": "fade",       "duration": 0.04},  # near-zero fade = hard cut
}


# ── Rhythm presets ─────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class RhythmPreset:
    name: str
    duration_pattern: List[float]    # cycles through these per-clip durations
    transitions: List[str]           # cycles through these transitions
    spacing: str                     # "slow" | "medium" | "tight"
    emotion_affinities: List[str]    # emotions this rhythm naturally matches


RHYTHM_PRESETS: Dict[str, RhythmPreset] = {
    "cinematic_breath": RhythmPreset(
        name="cinematic_breath",
        duration_pattern=[8.0, 6.0, 8.0, 5.0, 8.0],
        transitions=["fade", "dissolve", "fade", "circleopen", "fade"],
        spacing="slow",
        emotion_affinities=["calm", "ascending", "warm"],
    ),
    "fast_cuts": RhythmPreset(
        name="fast_cuts",
        duration_pattern=[2.5, 2.0, 2.0, 1.5, 2.0],
        transitions=["hard_cut", "slideleft", "hard_cut", "slideleft"],
        spacing="tight",
        emotion_affinities=["tension", "powerful"],
    ),
    "smooth_flow": RhythmPreset(
        name="smooth_flow",
        duration_pattern=[7.0, 6.0, 7.0, 6.0],
        transitions=["dissolve", "smoothleft", "dissolve", "smoothright"],
        spacing="medium",
        emotion_affinities=["intimate", "vulnerable", "release"],
    ),
    "dramatic": RhythmPreset(
        name="dramatic",
        duration_pattern=[6.0, 4.0, 2.0, 6.0, 8.0],
        transitions=["fade", "circleclose", "hard_cut", "fade", "circleopen"],
        spacing="medium",
        emotion_affinities=["breaking", "powerful"],
    ),
    "minimal": RhythmPreset(
        name="minimal",
        duration_pattern=[10.0, 8.0, 10.0],
        transitions=["fade", "fade", "fade"],
        spacing="slow",
        emotion_affinities=["vulnerable", "intimate", "calm"],
    ),
}

# Backward-compat alias: RHYTHMS[name] → transitions list
RHYTHMS: Dict[str, List[str]] = {k: v.transitions for k, v in RHYTHM_PRESETS.items()}

# Emotion → rhythm
EMOTION_RHYTHM: Dict[str, str] = {
    "tension":    "fast_cuts",
    "release":    "smooth_flow",
    "ascending":  "cinematic_breath",
    "breaking":   "dramatic",
    "calm":       "cinematic_breath",
    "intimate":   "minimal",
    "powerful":   "dramatic",
    "vulnerable": "smooth_flow",
    "warm":       "cinematic_breath",
}


def rhythm_from_emotion(emotion: str) -> str:
    """Map a HELEN emotion label to a rhythm preset name."""
    return EMOTION_RHYTHM.get(emotion, "cinematic_breath")


# ── Data model ─────────────────────────────────────────────────────────────────

@dataclass
class ClipSpec:
    src: str
    start: float = 0.0
    duration: float = 0.0       # 0 = assigned by rhythm preset / duration_target
    transition_out: str = "fade"
    label: str = ""


@dataclass
class AudioSpec:
    voiceover: str = ""
    music: str = ""
    music_volume: float = 0.15
    voiceover_delay: float = 1.0


@dataclass(frozen=True)
class AudioAlignment:
    voice_start: float      # absolute timeline position where voice starts
    music_fade_in: float    # always 0 — music starts at top
    music_fade_out: float   # position where music begins to fade (end - 2s)
    total_duration: float   # total video duration in seconds


@dataclass
class MontagePlanV1:
    plan_id: str
    duration_target: float
    clips: List[ClipSpec]
    audio: AudioSpec
    rhythm: str
    resolution: tuple = (1920, 1080)
    fps: int = 30
    authority: bool = False

    def __post_init__(self) -> None:
        if self.authority:
            raise ValueError("MontagePlanV1.authority must be False")

    @property
    def plan_hash(self) -> str:
        payload = _canonical({
            "plan_id":         self.plan_id,
            "duration_target": self.duration_target,
            "rhythm":          self.rhythm,
            "clips": [
                {"src": c.src, "start": c.start, "duration": c.duration,
                 "transition_out": c.transition_out}
                for c in self.clips
            ],
            "audio": {
                "voiceover": self.audio.voiceover,
                "music":     self.audio.music,
            },
        })
        return "sha256:" + hashlib.sha256(payload.encode()).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type":            "MONTAGE_PLAN_V1",
            "plan_id":         self.plan_id,
            "duration_target": self.duration_target,
            "rhythm":          self.rhythm,
            "clips": [
                {"src": c.src, "start": c.start, "duration": c.duration,
                 "transition_out": c.transition_out, "label": c.label}
                for c in self.clips
            ],
            "audio": {
                "voiceover":       self.audio.voiceover,
                "music":           self.audio.music,
                "music_volume":    self.audio.music_volume,
                "voiceover_delay": self.audio.voiceover_delay,
            },
            "authority": False,
        }


# ── Timeline entry ─────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class TimelineEntry:
    clip_index:      int
    src:             str
    label:           str
    clip_start:      float    # trim point inside source file
    clip_duration:   float    # how many seconds of this clip appear in output
    transition_in:   str      # name of transition from previous clip ("none" for first)
    trans_duration:  float    # duration of that incoming transition (0 for first)
    tl_start:        float    # absolute start time in output video (= xfade offset)
    tl_end:          float    # absolute end time (tl_start + clip_duration)


# ── Timeline solver ────────────────────────────────────────────────────────────

def compute_timeline(plan: MontagePlanV1) -> List[TimelineEntry]:
    """
    Solve absolute start/end times for every clip, accounting for transition overlaps.

    Key insight:
      tl_start[i] = sum(clip_duration[j] - trans_duration[j] for j in 0..i-1)

    where trans_duration[j] = duration of the transition AFTER clip j.

    This value IS the FFmpeg xfade `offset` for clip i.
    """
    entries: List[TimelineEntry] = []
    cursor = 0.0

    for i, clip in enumerate(plan.clips):
        if i == 0:
            trans_in_name = "none"
            trans_dur = 0.0
        else:
            prev = plan.clips[i - 1]
            t = TRANSITIONS.get(prev.transition_out, TRANSITIONS["fade"])
            trans_in_name = prev.transition_out
            trans_dur = t["duration"]

        entries.append(TimelineEntry(
            clip_index=i,
            src=clip.src,
            label=clip.label or Path(clip.src).stem,
            clip_start=clip.start,
            clip_duration=clip.duration,
            transition_in=trans_in_name,
            trans_duration=trans_dur,
            tl_start=round(cursor, 4),
            tl_end=round(cursor + clip.duration, 4),
        ))

        # Advance cursor: next clip overlaps by trans_after this clip
        if i < len(plan.clips) - 1:
            t_after = TRANSITIONS.get(clip.transition_out, TRANSITIONS["fade"])
            cursor += clip.duration - t_after["duration"]
        else:
            cursor += clip.duration

    return entries


def _timeline_hash(timeline: List[TimelineEntry]) -> str:
    payload = _canonical([
        {"i": e.clip_index, "src": e.src,
         "tl_start": e.tl_start, "tl_end": e.tl_end,
         "trans": e.transition_in, "trans_dur": e.trans_duration}
        for e in timeline
    ])
    return "sha256:" + hashlib.sha256(payload.encode()).hexdigest()


# ── Audio alignment ────────────────────────────────────────────────────────────

def align_audio(plan: MontagePlanV1, timeline: List[TimelineEntry]) -> AudioAlignment:
    """Compute timeline-anchored audio positions from solved clip durations."""
    total = timeline[-1].tl_end if timeline else plan.duration_target
    return AudioAlignment(
        voice_start=plan.audio.voiceover_delay,
        music_fade_in=0.0,
        music_fade_out=round(max(0.0, total - 2.0), 3),
        total_duration=round(total, 3),
    )


# ── Filter graph builder ───────────────────────────────────────────────────────

def _build_filter_graph(
    plan: MontagePlanV1,
    timeline: List[TimelineEntry],
    audio_align: AudioAlignment,
) -> Tuple[List[str], str, List[str], List[str]]:
    """
    Compile a deterministic FFmpeg filter_complex from the solved timeline.

    Returns:
        (input_flags, filter_complex_str, map_args, audio_enc_args)

    xfade offset = timeline[i].tl_start  (proven by the timeline solver invariant)
    """
    W, H = plan.resolution
    fps = plan.fps
    n = len(plan.clips)

    inputs: List[str] = []
    for clip in plan.clips:
        inputs += ["-i", clip.src]

    parts: List[str] = []

    # ── Step 1: prepare (scale + trim) each clip ──────────────────────────────
    for i, (clip, entry) in enumerate(zip(plan.clips, timeline)):
        trim = ""
        if clip.start > 0 or clip.duration > 0:
            s = clip.start
            d = clip.duration if clip.duration > 0 else 9999.0
            trim = f",trim=start={s}:duration={d},setpts=PTS-STARTPTS"
        parts.append(
            f"[{i}:v]settb=AVTB,fps={fps},"
            f"scale={W}:{H}:force_original_aspect_ratio=decrease,"
            f"pad={W}:{H}:(ow-iw)/2:(oh-ih)/2{trim}[pv{i}]"
        )

    # ── Step 2: compile xfade chain from solved timeline ─────────────────────
    if n == 1:
        parts.append("[pv0]null[vout]")
    else:
        prev = "pv0"
        for i in range(1, n):
            entry = timeline[i]
            t = TRANSITIONS.get(plan.clips[i - 1].transition_out, TRANSITIONS["fade"])
            ffmpeg_trans = t["ffmpeg"] or "fade"
            trans_dur    = t["duration"]
            offset       = entry.tl_start   # from solver — the ground truth

            tag = f"xf{i}" if i < n - 1 else "vout"
            parts.append(
                f"[{prev}][pv{i}]xfade=transition={ffmpeg_trans}:"
                f"duration={trans_dur}:offset={offset:.4f}[{tag}]"
            )
            prev = tag

    video_filter = ";\n    ".join(parts)

    # ── Step 3: audio with timeline-anchored fade ─────────────────────────────
    audio_parts: List[str] = []
    audio_map:   List[str] = []
    audio_idx = n

    if plan.audio.voiceover and os.path.exists(plan.audio.voiceover):
        inputs += ["-i", plan.audio.voiceover]
        delay_ms = int(audio_align.voice_start * 1000)
        audio_parts.append(
            f"[{audio_idx}:a]adelay={delay_ms}|{delay_ms},volume=1.5[vo]"
        )
        audio_map.append("[vo]")
        audio_idx += 1

    if plan.audio.music and os.path.exists(plan.audio.music):
        inputs += ["-i", plan.audio.music]
        fade_st  = int(audio_align.music_fade_out)
        total    = int(audio_align.total_duration)
        audio_parts.append(
            f"[{audio_idx}:a]volume={plan.audio.music_volume},"
            f"afade=t=out:st={fade_st}:d=2,"
            f"atrim=duration={total}[mus]"
        )
        audio_map.append("[mus]")

    if audio_map:
        video_filter += ";\n    " + ";\n    ".join(audio_parts)
        mix_n = len(audio_map)
        video_filter += (
            f";\n    {''.join(audio_map)}"
            f"amix=inputs={mix_n}:duration=longest:dropout_transition=3[aout]"
        )
        map_args  = ["-map", "[vout]", "-map", "[aout]"]
        audio_enc = ["-c:a", "aac", "-b:a", "192k"]
    else:
        map_args  = ["-map", "[vout]"]
        audio_enc = ["-an"]

    return inputs, video_filter, map_args, audio_enc


# ── Duration assignment ────────────────────────────────────────────────────────

def _assign_durations(
    specs: List[ClipSpec],
    preset: RhythmPreset,
    duration_target: float,
) -> None:
    """
    Fill in duration=0 clips using the rhythm duration pattern, scaled to hit target.

    Clips with explicit duration > 0 are left untouched.
    """
    unset = [i for i, s in enumerate(specs) if s.duration == 0]
    if not unset:
        return

    # Transition overhead (overlaps are reclaimed time)
    trans_overhead = sum(
        TRANSITIONS.get(specs[i].transition_out, TRANSITIONS["fade"])["duration"]
        for i in range(len(specs) - 1)
    )
    content_budget = duration_target + trans_overhead
    assigned = sum(s.duration for s in specs if s.duration > 0)
    remaining = content_budget - assigned

    pat = preset.duration_pattern
    raw = [pat[i % len(pat)] for i in unset]
    raw_total = sum(raw)
    scale = remaining / raw_total if raw_total > 0 else 1.0

    for idx, clip_i in enumerate(unset):
        specs[clip_i].duration = round(raw[idx] * scale, 3)


# ── Plan builder ───────────────────────────────────────────────────────────────

def build_montage_plan(
    clips: List[str | ClipSpec],
    duration_target: float = 30.0,
    voiceover: str = "",
    music: str = "",
    music_volume: float = 0.15,
    rhythm: str = "cinematic_breath",
    emotion: str = "",
    plan_id: str = "",
    labels: Optional[List[str]] = None,
) -> MontagePlanV1:
    """
    Build a MONTAGE_PLAN_V1 from clip paths or ClipSpec objects.

    If `emotion` is provided, the rhythm is resolved from EMOTION_RHYTHM unless
    `rhythm` is explicitly non-default.  Duration patterns come from the rhythm
    preset and are scaled to hit `duration_target`.
    """
    # Emotion overrides rhythm if not explicitly set
    resolved_rhythm = (
        rhythm_from_emotion(emotion)
        if emotion and rhythm == "cinematic_breath"
        else rhythm
    )

    preset = RHYTHM_PRESETS.get(resolved_rhythm, RHYTHM_PRESETS["cinematic_breath"])

    if not plan_id:
        src_list = [c if isinstance(c, str) else c.src for c in clips]
        plan_id  = "mp_" + hashlib.sha256("".join(src_list).encode()).hexdigest()[:12]

    trans_cycle = preset.transitions
    specs: List[ClipSpec] = []
    for i, c in enumerate(clips):
        if isinstance(c, ClipSpec):
            specs.append(c)
        else:
            specs.append(ClipSpec(
                src=c,
                transition_out=trans_cycle[i % len(trans_cycle)],
                label=labels[i] if labels and i < len(labels) else Path(c).stem,
            ))

    # Assign transitions for ClipSpec objects that still have the default "fade"
    # only if they were passed in (not created above), i.e., user didn't set them
    for i, spec in enumerate(specs):
        if spec.transition_out == "fade" and isinstance(clips[i] if i < len(clips) else None, str):
            spec.transition_out = trans_cycle[i % len(trans_cycle)]

    _assign_durations(specs, preset, duration_target)

    return MontagePlanV1(
        plan_id=plan_id,
        duration_target=duration_target,
        clips=specs,
        audio=AudioSpec(
            voiceover=voiceover,
            music=music,
            music_volume=music_volume,
        ),
        rhythm=resolved_rhythm,
    )


# ── Stub renderer (no ffmpeg) ──────────────────────────────────────────────────

def render_montage_stub(plan: MontagePlanV1, output_path: str) -> Dict[str, Any]:
    """Hash-only render for CI / tests — no subprocess, no ffmpeg."""
    timeline    = compute_timeline(plan)
    audio_align = align_audio(plan, timeline)

    payload    = _canonical(plan.to_dict())
    video_hash = "sha256:" + hashlib.sha256(payload.encode()).hexdigest()

    return {
        "type":           "MONTAGE_RECEIPT_V1",
        "plan_id":        plan.plan_id,
        "plan_hash":      plan.plan_hash,
        "timeline_hash":  _timeline_hash(timeline),
        "clip_count":     len(plan.clips),
        "duration":       audio_align.total_duration,
        "rhythm":         plan.rhythm,
        "output_path":    output_path,
        "video_hash":     video_hash,
        "audio_hash":     "",
        "clips":          [
            {"src": e.src, "hash": "", "tl_start": e.tl_start, "tl_end": e.tl_end}
            for e in timeline
        ],
        "rendered_at":    _now_utc(),
        "stub":           True,
        "success":        True,
        "authority":      False,
    }


# ── Real renderer (ffmpeg) ─────────────────────────────────────────────────────

def render_montage(
    plan: MontagePlanV1,
    output_path: str,
    timeout: int = 600,
) -> Dict[str, Any]:
    """
    Render a MONTAGE_PLAN_V1 to MP4 using a compiled FFmpeg filter graph.

    Timeline is solved first, then the filter graph is compiled from it.
    Returns MONTAGE_RECEIPT_V1 with sha256 of every input, the timeline, and output.
    """
    timeline    = compute_timeline(plan)
    audio_align = align_audio(plan, timeline)

    inputs, filter_str, map_args, audio_enc = _build_filter_graph(plan, timeline, audio_align)

    cmd = (
        ["ffmpeg", "-y"] + inputs
        + ["-filter_complex", filter_str]
        + map_args
        + ["-c:v", "libx264", "-preset", "fast", "-crf", "20", "-pix_fmt", "yuv420p"]
        + audio_enc
        + [output_path]
    )

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)

    # Hash inputs
    clip_receipts: List[Dict[str, Any]] = []
    for e in timeline:
        h = _sha256_file(e.src) if os.path.exists(e.src) else ""
        clip_receipts.append({
            "src":      e.src,
            "hash":     h,
            "tl_start": e.tl_start,
            "tl_end":   e.tl_end,
        })

    audio_hash = ""
    if plan.audio.voiceover and os.path.exists(plan.audio.voiceover):
        audio_hash = _sha256_file(plan.audio.voiceover)

    video_hash     = ""
    output_size_kb = 0
    if os.path.exists(output_path):
        video_hash     = _sha256_file(output_path)
        output_size_kb = os.path.getsize(output_path) // 1024

    receipt: Dict[str, Any] = {
        "type":           "MONTAGE_RECEIPT_V1",
        "plan_id":        plan.plan_id,
        "plan_hash":      plan.plan_hash,
        "timeline_hash":  _timeline_hash(timeline),
        "clip_count":     len(plan.clips),
        "duration":       audio_align.total_duration,
        "rhythm":         plan.rhythm,
        "output_path":    output_path,
        "video_hash":     video_hash,
        "audio_hash":     audio_hash,
        "clips":          clip_receipts,
        "rendered_at":    _now_utc(),
        "stub":           False,
        "success":        result.returncode == 0,
        "authority":      False,
    }

    if result.returncode == 0:
        receipt["output_size_kb"] = output_size_kb
    else:
        receipt["error"] = result.stderr[-800:] if result.stderr else "unknown"

    return receipt
